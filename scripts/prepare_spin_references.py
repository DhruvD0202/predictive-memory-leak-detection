"""Build a focused Springer bibliography from the previously audited sources."""
from pathlib import Path
import concurrent.futures
import json
import re
import urllib.request
import urllib.parse

ROOT=Path(__file__).resolve().parents[1]
KEEP=[1,2,3,4,5,6,8,9,10,11,12,14,17,19,20,21,22,24,25,26,28,29,30,31,32,33,35,36,39,40,41,42,43,44,45,46]

def get_record(item):
    number,entry=item
    match=re.search(r'https://doi.org/([^\s\]]+)',entry)
    doi=match.group(1) if match else None
    result={'original_reference':number,'original_entry':entry,'doi':doi}
    if doi and not doi.startswith(('10.48550/','10.5281/')):
        try:
            url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
            req=urllib.request.Request(url,headers={'User-Agent':'AcademicManuscriptBibliography/1.0'})
            with urllib.request.urlopen(req,timeout=40) as response:
                result['metadata']=json.load(response)['message']
        except Exception as exc:
            result['metadata_error']=str(exc)
    return result

def tex(s):
    return str(s).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')

def main():
    source=(ROOT/'paper/Predictive_Memory_Leak_Detection_Draft.md').read_text(encoding='utf-8')
    entries={int(n):entry for n,entry in re.findall(r'^\[(\d+)\] (.+)$',source,re.M)}
    audit=ROOT/'paper/spin2027_reference_metadata.json'
    if audit.exists():
        records=json.loads(audit.read_text(encoding='utf-8'))
        assert [r['original_reference'] for r in records]==KEEP
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            records=list(pool.map(get_record,[(n,entries[n]) for n in KEEP]))
    audit.write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    bibliography=[]
    for record in records:
        n=record['original_reference']; entry=record['original_entry']; metadata=record.get('metadata',{})
        if n in (24,25):
            authors,title,year,publisher,edition=(
                ('Box, George E. P. and Jenkins, Gwilym M. and Reinsel, Gregory C.',
                 'Time Series Analysis: Forecasting and Control','2008','Wiley','4') if n==24 else
                ('Hyndman, Rob J. and Athanasopoulos, George','Forecasting: Principles and Practice','2021','OTexts','3'))
            fields={'author':authors,'title':title,'year':year,'publisher':publisher,'edition':edition}
            if record['doi']: fields['doi']=record['doi']
            else: fields['url']='https://otexts.com/fpp3/'
            kind='book'
        elif metadata:
            authors=' and '.join(a.get('family','')+', '+a.get('given','') for a in metadata.get('author',[]))
            # Retain the audited issue/conference year instead of online/deposit dates.
            years=re.findall(r'\b(?:19|20)\d{2}\b',entry.split(' [')[0])
            year=str(years[-1])
            if n==45: year='2023'
            title=metadata['title'][0]
            subtitles=metadata.get('subtitle',[])
            if subtitles and subtitles[0].lower() not in title.lower():
                title=title.rstrip(':')+': '+subtitles[0]
            fields={'author':authors,'title':title,'year':year,'doi':record['doi']}
            kind='article' if metadata.get('type')=='journal-article' else 'inproceedings'
            fields['journal' if kind=='article' else 'booktitle']=metadata.get('container-title',[''])[0]
            for key in ['volume','issue','page']:
                if metadata.get(key): fields[{'issue':'number','page':'pages'}.get(key,key)]=str(metadata[key]).replace('-', '--') if key=='page' else metadata[key]
            if kind=='inproceedings' and metadata.get('publisher'): fields['publisher']=metadata['publisher']
        else:
            match=re.match(r'(.+?), "(.+?)"[, ]+(.+)',entry)
            assert match,(n,entry)
            author_text,title,tail=match.groups()
            title=title.rstrip(',')
            authors=[]
            for a in re.split(r', | and ',author_text):
                pieces=a.split(' ')
                split=next((i for i,x in enumerate(pieces) if not x.endswith('.')),len(pieces)-1)
                authors.append(' '.join(pieces[split:])+', '+' '.join(pieces[:split]))
            fields={'author':' and '.join(authors),'title':title}
            year=re.search(r'\b(?:19|20)\d{2}\b',tail).group()
            fields['year']=year
            kind='misc'
            if n in (1,5,6):
                arxiv=re.search(r'arXiv:(\d+\.\d+)',tail).group(1)
                fields['howpublished']='arXiv preprint arXiv:'+arxiv
            elif n==3:
                fields['howpublished']='Zenodo, version 1.0'
            elif n==2:
                kind='article'; fields.update(journal='International Journal of Nonlinear Analysis and Applications',volume='13',number='2',pages='2121--2131')
            elif n==8:
                kind='inproceedings'; fields.update(booktitle='International Symposium on Software Reliability Engineering',pages='84--93',publisher='IEEE')
            elif n==21:
                kind='inproceedings'; fields.update(booktitle='16th USENIX Symposium on Operating Systems Design and Implementation (OSDI)',pages='109--125',publisher='USENIX Association')
            elif n==43:
                kind='inproceedings'; fields.update(booktitle='Advances in Neural Information Processing Systems',volume='31')
            else:
                # Failed metadata retrieval must be repaired before use.
                raise RuntimeError(f'Metadata unavailable for reference {n}: '+str(record.get('metadata_error')))
            if record['doi']: fields['doi']=record['doi']
            else:
                urls=re.findall(r'\]\((https?://[^)]+)\)',entry)
                if urls: fields['url']=urls[-1]
        if n==5: fields['year']='2018'; fields['note']='Revised 2019'
        if n==4:
            fields['year']='2019'
            fields['booktitle']='Euro-Par 2018: Parallel Processing Workshops'
            fields['series']='Lecture Notes in Computer Science'
            fields['volume']='11339'
        if n==2: fields['year']='2022'
        # Crossref sometimes retains only the starting page / early-access pages.
        if n==33: fields['pages']='245--259'
        if n==45: fields.update(volume='35',number='3',pages='2421--2429',year='2023')
        # Engineering proceedings shorten lists longer than six authors.
        names=fields['author'].split(' and ')
        if len(names)>6: fields['author']=' and '.join(names[:6]+['others'])
        bibliography.append('@'+kind+'{ref'+str(n)+',\n'+',\n'.join('  '+key+' = {'+(str(value) if key in ['doi','url'] else ('{'+tex(value)+'}' if key=='title' else tex(value)))+'}' for key,value in fields.items())+'\n}')
    target=ROOT/'paper/spin2027/references.bib'
    target.write_text('\n\n'.join(bibliography)+'\n',encoding='utf-8')
    prior=(ROOT/'paper/REFERENCE_AUDIT.md').read_text(encoding='utf-8')
    rows=[line for line in prior.splitlines() if (m:=re.match(r'\| (\d+) \|',line)) and int(m[1]) in KEEP]
    citation_map='''# SPIN revision citation map

Checked 16 October 2026. All 36 retained works are cited; no uncited bibliography entries remain. Keys `refN` refer to the earlier audit number below; Springer assigns final printed numbers alphabetically. This map records limited claim support, not a claim to have read every subscription full text. Publisher-deposited metadata was refreshed for 27 works. The Assi article was checked against its local publisher PDF because its DOI metadata endpoint returned 404. Full titles/subtitles and final pages were restored where metadata was incomplete.

The revised survey uses these works for method, data and evaluation context. It does not import their numerical results or claim to reproduce their algorithms. All project scores come from saved experimental outputs. The comparison table describes boundaries relevant to this study, not unsupported general weaknesses of prior work.

| Earlier key | Scope supported | Primary evidence / reading scope |
|---|---|---|
'''+ '\n'.join(rows)+'\n'
    (ROOT/'paper/SPIN2027_CITATION_MAP.md').write_text(citation_map,encoding='utf-8')
    print('Wrote',len(records),'references; publisher metadata retrieved for',sum('metadata' in r for r in records))
    print('Failed metadata:',[(r['original_reference'],r.get('metadata_error')) for r in records if 'metadata_error' in r])

if __name__=='__main__': main()
