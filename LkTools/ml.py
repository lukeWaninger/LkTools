if 'itertools' not in globals():
    import itertools
if 'np' not in globals():
    import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score, accuracy_score, confusion_matrix, classification_report, log_loss, f1_score, precision_score, recall_score
  
def generate_grid(dkt):
    for k, v in dkt.items():
        if not isinstance(v, (list, np.ndarray)):
            dkt[k] = [v]
            
    grid = list(itertools.product(
        *[[{i: j} for j in k] for i, k in dkt.items()]
    ))

    return [
        {k[0]:k[1] for k in [list(ti.items())[0] for ti in candidate_set]}
        for candidate_set in grid
    ]

def eval_metrics(actual, pred, inc=None):
    if inc is not None:
        result = {}
        if 'recall' in inc:
            result['recall'] = recall_score(actual, pred)
    else:   
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        auc = roc_auc_score(actual, pred)

        pred = [1 if p >= .5 else 0 for p in pred]
        f1 = f1_score(actual, pred)
        pre = precision_score(actual, pred)
        rec = recall_score(actual, pred)
        result = {'rmse':rmse, 'mae':mae, 'r2':r2, 'auc':auc, 'f1':f1, 'precision':pre, 'recall':rec}

    return result
