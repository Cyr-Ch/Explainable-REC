class CoderAgent:
    def __init__(self, icl_examples, llm=None):
        self.icl=icl_examples; self.llm=llm
    def propose_modifications(self, q):
        q=q.lower(); import re
        def pct():
            import re
            m=re.search(r'(-?\d+(?:\.\d+)?)\s*%', q); return float(m.group(1)) if m else None
        p=pct(); ops=[]
        if 'import' in q and p is not None: ops.append({'op':'scale_series','target':'Pimp','scale_pct':p})
        elif 'export' in q and p is not None: ops.append({'op':'scale_series','target':'Pexp','scale_pct':p})
        elif 'pv' in q and p is not None: ops.append({'op':'scale_series','target':'PV','scale_pct':p})
        elif 'shift' in q and p is not None:
            hh=re.findall(r'(?:from|at)\s+(\d{1,2}).*?(?:to)\s+(\d{1,2})', q)
            a,b=(13,14) if not hh else (int(hh[0][0]), int(hh[0][1]))
            ops.append({'op':'shift_load','percentage':p,'from_hour':a,'to_hour':b})
        return {'ops':ops,'explanation':'rule-based'}
