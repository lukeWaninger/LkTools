import datetime as dt
import multiprocessing as mul
import  time

import numpy as np
from tqdm import tqdm_notebook as tqdm


class PcMap():
    def __init__(self, func, args, n_cons=None, **kwargs):
        self.__func = func
        self.__args = args

        n = mul.cpu_count()
        self.__n_cons = int(np.ceil(n/2)) if n_cons is None or n_cons <= 0 else n_cons
        self.__man = mul.Manager()

        self.__task_qu = self.__man.Queue()
        self.__results_qu = self.__man.Queue()

        self.pbar = None
        self.results = []
        self.failures = []

    @property
    def n_jobs(self):
        return self.__n_cons

    @staticmethod
    def __consumer(func, task_qu, results_qu):
        finished = False
        while not finished:
            task = task_qu.get()
            if isinstance(task, str) and task == 'END':
                finished = True
            else:
                try:
                    r = {
                        'result': func(*task),
                        'success': 1
                    }
                except Exception as ex:
                    r = {
                        'result': {
                            'args': task,
                            'exception': ex
                        },
                        'success': 0
                    }
                results_qu.put(r)

    def tracker(self, description=None):
        self.pbar = tqdm(total=len(self.__args))
        if description is not None and isinstance(description, str):
            self.pbar.set_description(description)
        return self.pbar
    
    def start(self, delay=None, intermediate_func=None, interval=None, intermediate_args=None):
        # generate consumers
        consumers = [
            mul.Process(target=self.__consumer, args=(self.__func, self.__task_qu, self.__results_qu))
            for i in range(self.__n_cons)
        ]

        # load the tasks and termination flags
        [self.__task_qu.put(a) for a in self.__args]
        [self.__task_qu.put('END') for i in range(self.__n_cons)]
        
        # start the consumers
        for c in consumers:
            c.start()
            if delay is not None:
                time.sleep(delay)
        
        # manage results
        n_tasks = len(self.__args)
        last_intermediate_run = dt.datetime.now()

        while n_tasks > 0:
            # empty the results qu
            while not self.__results_qu.empty():
                t = self.__results_qu.get()
                if t['success'] == 1:
                    self.results.append(t['result'])
                else:
                    self.failures.append(t['result'])
                
                n_tasks -= 1
                if self.pbar is not None: 
                    self.pbar.update(1)

            # the intermediate function
            if intermediate_func is not None:
                now = dt.datetime.now()
                if int(np.ceil((now - last_intermediate_run).total_seconds())) > interval:
                    last_intermediate_run = now
                    intermediate_func(*intermediate_args) if intermediate_args is not None else intermediate_func()

        # round-robin check child status
        for i in range(len(consumers)):
            p = consumers[i]
            if not p.is_alive():
                p.join()
                del p
            else:
                p.terminate()
                p.join()
                del p

        if self.pbar is not None:
            self.pbar.set_description('complete')
        return [r for r in self.results]