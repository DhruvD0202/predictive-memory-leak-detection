import copy
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import lstm_forecasting as experiment


class LSTMIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.device,cls.runtime=experiment.configure_runtime('cpu')

    def test_window_ends_at_origin_and_is_invariant_to_future_values(self):
        x=np.arange(300*3,dtype=np.float32).reshape(300,3)
        before=experiment.gather_history(x,np.array([100]),60)
        np.testing.assert_array_equal(before[0],x[41:101])
        x[101:]=1e10
        np.testing.assert_array_equal(before,experiment.gather_history(x,np.array([100]),60))

    def test_state_is_not_carried_between_windows(self):
        experiment.seed_everything(42)
        model=experiment.MemoryLSTM(3,4).eval()
        first=torch.randn(1,12,3); unrelated=torch.randn(1,12,3)
        with torch.inference_mode():
            a=model(first); model(unrelated); b=model(first)
            combined=model(torch.cat([first,unrelated],dim=0))[0]
        torch.testing.assert_close(a,b,rtol=0,atol=0)
        torch.testing.assert_close(a[0],combined,rtol=1e-6,atol=1e-7)

    def test_weights_reload_preserves_forecasts(self):
        experiment.seed_everything(42)
        a=experiment.MemoryLSTM(3,4).eval(); x=torch.randn(4,12,3)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'weights.pt'
            experiment.atomic_torch_save(experiment.cpu_weights(a),path)
            b=experiment.MemoryLSTM(3,4).eval()
            b.load_state_dict(torch.load(path,weights_only=True))
            with torch.inference_mode(): torch.testing.assert_close(a(x),b(x),rtol=0,atol=0)

    def test_optimizer_can_reduce_loss_on_a_small_learnable_fixture(self):
        experiment.seed_everything(42)
        model=experiment.MemoryLSTM(2,4)
        x=torch.randn(16,8,2); target=x[:,-1,0]
        optimizer=torch.optim.Adam(model.parameters(),lr=.03)
        loss_fn=torch.nn.MSELoss()
        initial=float(loss_fn(model(x),target).detach())
        for _ in range(40):
            optimizer.zero_grad(); loss=loss_fn(model(x),target); loss.backward(); optimizer.step()
        final=float(loss_fn(model(x),target).detach())
        self.assertLess(final,initial*.5)

    def test_early_stopping_uses_validation_only_and_handles_ties(self):
        values=[2.,1.,1.,1.,1.,1.]
        history=[{'validation_rmse_fraction':x} for x in values]
        self.assertFalse(experiment.should_stop(history[:-1],4))
        self.assertTrue(experiment.should_stop(history,4))

    def fixture(self):
        t=np.arange(240)
        y=(.3+.07*np.sin(t/10)).astype(np.float32)
        mean=float(y[:120].mean()); scale=float(y[:120].std())
        arrays={'features':np.column_stack([(y-mean)/scale,np.cos(t/10)]).astype(np.float32),
                'target_memory_pressure':y,'target_mean':mean,'target_std':scale,
                'split_code':np.r_[np.zeros(120),np.ones(60),np.full(60,2)].astype(np.int8)}
        windows=[]
        for split,start,end in [('train',0,120),('validation',120,180),('test',180,240)]:
            for o in range(start+7,end-2): windows.append({'split':split,'origin_index':o,'target_index':o+2})
        info={'dataset':'westermo_fixture','feature_names':['memory_pressure','context'],'history_steps':8,'horizon_steps':2}
        settings={**experiment.SETTINGS,'hidden_units':4,'batch_size':32,'max_epochs':3,'westermo_training_stride':1}
        return arrays,pd.DataFrame(windows),info,settings

    def test_interrupted_training_resumes_to_identical_weights(self):
        arrays,windows,info,settings=self.fixture()
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            full=Path(folder)/'full'; resumed=Path(folder)/'resumed'
            a,fa=experiment.train_recording(arrays,windows,info,full,self.device,self.runtime,settings)
            original=experiment.atomic_torch_save
            def interrupt_after_checkpoint(value,path):
                original(value,path)
                if Path(path).name=='last_checkpoint.pt' and value['epoch']==1:
                    raise InterruptedError('Simulated interruption after a persisted epoch')
            with patch.object(experiment,'atomic_torch_save',interrupt_after_checkpoint):
                with self.assertRaises(InterruptedError):
                    experiment.train_recording(arrays,windows,info,resumed,self.device,self.runtime,settings)
            b,fb=experiment.train_recording(arrays,windows,info,resumed,self.device,self.runtime,settings)
            for key in a.state_dict(): torch.testing.assert_close(a.state_dict()[key],b.state_dict()[key],rtol=0,atol=0)
            self.assertEqual(fa['best_epoch'],fb['best_epoch'])
            self.assertEqual(fa['best_validation_rmse_fraction'],fb['best_validation_rmse_fraction'])

    def test_future_test_values_cannot_change_trained_weights_or_selection(self):
        arrays,windows,info,settings=self.fixture()
        changed=copy.deepcopy(arrays)
        changed['features'][180:]=10000
        changed['target_memory_pressure'][180:]=10000
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            a,fa=experiment.train_recording(arrays,windows,info,Path(folder)/'original',self.device,self.runtime,settings)
            b,fb=experiment.train_recording(changed,windows,info,Path(folder)/'changed',self.device,self.runtime,settings)
            for key in a.state_dict(): torch.testing.assert_close(a.state_dict()[key],b.state_dict()[key],rtol=0,atol=0)
            self.assertEqual(fa['best_epoch'],fb['best_epoch'])
            self.assertEqual(fa['best_validation_rmse_fraction'],fb['best_validation_rmse_fraction'])


if __name__=='__main__': unittest.main(verbosity=2)
