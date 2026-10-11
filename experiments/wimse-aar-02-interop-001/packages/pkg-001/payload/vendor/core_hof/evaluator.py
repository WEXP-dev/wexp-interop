"""Core-01 §§8.1–8.6 on HOF admitted inputs; PARTIAL, not general conformance.

This module consumes normalized input only; no envelope, source or mapper API.
"""
from itertools import combinations
import json

ORDER=['observation','intent','invocation','execution']

def uniq(values):
    return [json.loads(k) for k in sorted({json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False) for x in values})]

def le(a,b):return ORDER.index(a['base'])<=ORDER.index(b['base']) and set(a['qualifiers'])<=set(b['qualifiers'])

def appraise(inp):
    boundary=inp['boundary_finding'];asserted=inp['asserted_claim']
    usable=boundary['status']=='supported' and boundary['target_binding']=='supported'
    entries=[];premises={}
    for f in inp['base_findings']:
        if not (usable and f['target_binding']=='supported' and f['semantic_validation']=='supported' and ORDER.index(f['base'])<=ORDER.index(boundary['ceiling_base'])):continue
        qs=[q for q in inp['qualifier_findings'] if q['qualified_base']==f['base'] and q['target_binding']=='supported' and q['semantic_validation']=='supported' and q['independence_validation']=='supported']
        names=sorted(q['qualifier'] for q in qs)
        for count in range(len(names)+1):
            for combo in combinations(names,count):
                claim={'base':f['base'],'qualifiers':list(combo)}
                used=[boundary,f]+[q for q in qs if q['qualifier'] in combo]
                entries.append({'claim':claim,'basis_refs':uniq([v for x in used for v in x['basis_refs']]),'limitations':uniq([v for x in used for v in x['limitations']])})
                premises[json.dumps(claim,sort_keys=True)]=used
    supported=uniq([e['claim'] for e in entries]);maximal=[c for c in supported if not any(c!=d and le(c,d) for d in supported)]
    reasons=[];gaps=[]
    def gap(token,f,claims=None):
        gaps.append({'token':token,'target':inp['target'],'evaluation_context_ref':inp['evaluation_context']['id'],
                     'affected_claims':[asserted] if claims is None else claims,'basis_refs':f.get('basis_refs',[]),'limitations':f.get('limitations',[])})
    def binding(f,token):
        if f['target_binding']=='unsupported':reasons.append('E_EVIDENCE_NOT_BOUND')
        if f['target_binding']=='not-evaluated':gap(token,f)
    if boundary['status']=='unsupported':reasons.append('E_BOUNDARY_NOT_SUPPORTED')
    if boundary['status']=='not-evaluated':gap('E_BOUNDARY_NOT_EVALUATED',boundary)
    binding(boundary,'E_BOUNDARY_NOT_EVALUATED')
    base=next((f for f in inp['base_findings'] if f['base']==asserted['base']),None)
    required=[boundary]
    if base is None:reasons.append('E_MISSING_REQUIRED_EVIDENCE')
    else:
        required.append(base);binding(base,'E_BASE_NOT_EVALUATED')
        if base['semantic_validation']=='unsupported':reasons.append('E_EXACT_CLAIM_NOT_SUPPORTED')
        if base['semantic_validation']=='not-evaluated':gap('E_BASE_NOT_EVALUATED',base)
        if usable and ORDER.index(base['base'])>ORDER.index(boundary['ceiling_base']):reasons.append('E_BASE_EXCEEDS_BOUNDARY')
    for name in asserted['qualifiers']:
        q=next((q for q in inp['qualifier_findings'] if q['qualifier']==name and q['qualified_base']==asserted['base']),None)
        if q is None:reasons.append('E_MISSING_REQUIRED_EVIDENCE');continue
        required.append(q);binding(q,'E_IV_NOT_EVALUATED')
        if q['semantic_validation']=='unsupported':reasons.append('E_IV_NOT_SUPPORTED')
        if q['independence_validation']=='unsupported':reasons.append('E_INDEPENDENCE_NOT_ESTABLISHED')
        if 'not-evaluated' in (q['semantic_validation'],q['independence_validation']):gap('E_IV_NOT_EVALUATED',q)
    exact=asserted in supported;blocked=False
    def applies(e,cs):return e['affected_claims']=='all-admissible-claims' or any(c in e['affected_claims'] for c in cs)
    for c in inp['counter_evidence']:
        if not applies(c,[asserted]):continue
        if c['status'] in ('not-evaluated','unresolved-material','defeating'):
            blocked=True;reasons.extend(c['reasons'])
            if c['status']=='not-evaluated':gap('E_COUNTER_EVIDENCE_NOT_EVALUATED',c,c['affected_claims'])
            else:reasons.append('E_COUNTER_EVIDENCE_UNRESOLVED' if c['status']=='unresolved-material' else 'E_COUNTER_EVIDENCE_DEFEATING')
    used=required+[f for group in premises.values() for f in group]
    for f in used:reasons.extend(f['reasons'])
    for g in inp['profile_evaluation_gaps']:
        if applies(g,[asserted]+supported):gaps.append(g)
    inherited=list(inp['inherited_limitations'])+boundary['limitations']
    for f in used:inherited.extend(f['limitations'])
    for e in inp['counter_evidence']+inp['profile_evaluation_gaps']:
        if applies(e,[asserted]+supported):inherited.extend(e['limitations'])
    def relation(c):
        return 'equal' if c==asserted else 'support-below-claim' if le(c,asserted) else 'support-above-claim' if le(asserted,c) else 'incomparable'
    return {'semantics_version':'wexp-core-1','verdict':'accept' if exact and not blocked else 'downgrade',
        'fatal_reasons':[],'target':inp['target'],'asserted_claim':asserted,'asserted_claim_supported':exact,
        'support_entries':uniq(entries),'supported_claims':supported,'maximal_supported_claims':uniq(maximal),
        'support_relations':uniq([{'supported_claim':c,'relation':relation(c)} for c in maximal]),
        'boundary_ceiling':boundary['ceiling_base'] if usable else None,'boundary_grounding':boundary['grounding'],
        'recorder_relations':inp['recorder_relations'],'substantive_reasons':sorted(set(reasons)),
        'evaluation_gaps':sorted({g['token'] for g in gaps}),'evaluation_gap_entries':uniq(gaps),
        'counter_evidence':inp['counter_evidence'],'inherited_limitations':uniq(inherited),
        'evaluation_context':inp['evaluation_context'],'evaluation_scope':inp['evaluation_scope']}
