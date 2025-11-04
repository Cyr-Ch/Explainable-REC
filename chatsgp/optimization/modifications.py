def apply_modifications(data, ops):
    for op in ops:
        if op['op']=='scale_series':
            tgt=op['target']; pct=float(op['scale_pct']);
            if tgt in ('Load','PV'): data[tgt]=data[tgt]*(100.0+pct)/100.0
            elif tgt=='Pimp': data['Load']=data['Load']*(100.0+pct)/100.0
            elif tgt=='Pexp': data['PV']=data['PV']*(100.0+pct)/100.0
        elif op['op']=='shift_load':
            perc=float(op['percentage'])/100.0; a=int(op['from_hour']); b=int(op['to_hour']); amt=data['Load'][a]*perc; data['Load'][a]-=amt; data['Load'][b]+=amt
