"""Local research dashboard. Run: python app.py --no-browser."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
from urllib.parse import parse_qs, urlsplit
import webbrowser

from src.demo_service import DATASETS, LiveMonitor, ReplayRepository, json_bytes, prepare_inputs

ROOT = Path(__file__).resolve().parent


def make_server(root=ROOT, port=8765, repository=None, monitor=None):
    root = Path(root)
    repo = repository or ReplayRepository(root)
    live = monitor or LiveMonitor(root)
    token = secrets.token_urlsafe(24)
    static = {'/': root / 'dashboard/index.html', '/app.js': root / 'dashboard/app.js',
              '/styles.css': root / 'dashboard/styles.css', '/favicon.svg': root / 'dashboard/favicon.svg'}
    for dataset in DATASETS:
        static[f'/figures/{dataset}-learning.png'] = root / f'results/lstm_colab/{dataset}/learning_curve.png'
    static.update({'/figures/errors.png': root / 'results/lstm_colab/test_error_comparison.png',
                   '/figures/warnings.png': root / 'results/warnings_colab/antarex_warning_comparison.png'})

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            if str(args[1]) not in ('200', '204'):
                super().log_message(fmt, *args)

        def allowed_host(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

        def send(self, status, content, kind='application/json; charset=utf-8', filename=None):
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
            if filename:
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if not self.allowed_host():
                return self.send(403, json_bytes({'error': 'Use the localhost dashboard address'}))
            parsed = urlsplit(self.path)
            query = {key: value[-1] for key, value in parse_qs(parsed.query).items()}
            try:
                if parsed.path in static:
                    path = static[parsed.path]
                    return self.send(200, path.read_bytes(), mimetypes.guess_type(path)[0] or 'application/octet-stream')
                if parsed.path == '/api/metadata':
                    return self.send(200, json_bytes({**repo.metadata(), 'token': token}))
                if parsed.path in ('/api/replay', '/api/export/replay'):
                    dataset = query.get('dataset', 'antarex_mono')
                    index, window = int(query.get('index', '0')), int(query.get('window', '360'))
                    if parsed.path.endswith('/replay') and parsed.path.startswith('/api/export'):
                        return self.send(200, repo.export(dataset, index, window), 'text/csv; charset=utf-8', f'{dataset}-replay-window.csv')
                    return self.send(200, json_bytes(repo.replay(dataset, index, window)))
                if parsed.path == '/api/live':
                    return self.send(200, json_bytes(live.snapshot()))
                if parsed.path == '/api/export/live':
                    return self.send(200, live.export(), 'text/csv; charset=utf-8', 'local-telemetry.csv')
                self.send(404, json_bytes({'error': 'Not found'}))
            except (ValueError, KeyError, TypeError) as exc:
                self.send(400, json_bytes({'error': str(exc)}))
            except Exception as exc:
                self.log_error('%s', exc)
                self.send(500, json_bytes({'error': 'Could not load this resource. Check the dashboard terminal.'}))

        def do_POST(self):
            origin = self.headers.get('Origin')
            allowed_origins = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}
            if not self.allowed_host() or (origin and origin not in allowed_origins) or self.headers.get('X-Demo-Token') != token:
                return self.send(403, json_bytes({'error': 'Open this action from the local dashboard'}))
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 <= size <= 4096 or self.headers.get_content_type() != 'application/json':
                    raise ValueError('Expected a small JSON request')
                body = json.loads(self.rfile.read(size) or b'{}')
                if not isinstance(body, dict):
                    raise ValueError('Expected a JSON object')
                if self.path == '/api/live/start':
                    result = live.start(float(body.get('threshold', .8)))
                elif self.path == '/api/live/stop':
                    result = live.stop()
                elif self.path == '/api/infer':
                    result = repo.infer(body.get('dataset', ''), int(body.get('index', -1)))
                else:
                    return self.send(404, json_bytes({'error': 'Not found'}))
                self.send(200, json_bytes(result))
            except (ValueError, TypeError, json.JSONDecodeError, ImportError) as exc:
                self.send(400, json_bytes({'error': str(exc)}))
            except Exception as exc:
                self.log_error('%s', exc)
                self.send(500, json_bytes({'error': 'Action failed. Check the dashboard terminal.'}))

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    server.repository, server.monitor = repo, live
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--prepare', type=Path, help='Restore the verified preprocessing ZIP for on-demand model inference')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535')
    if args.prepare:
        print('Prepared model inputs:', prepare_inputs(args.prepare, ROOT), flush=True)
    print('Checking saved experiment files...', flush=True)
    try:
        server = make_server(port=args.port)
    except (ValueError, FileNotFoundError, OSError) as exc:
        parser.exit(1, f'Cannot start dashboard: {exc}\nSee README.md for setup or use another --port.\n')
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Dashboard ready: {url}\nPress Ctrl+C to stop. Live collection starts only when requested.', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.monitor.stop()
        server.server_close()


if __name__ == '__main__':
    main()
