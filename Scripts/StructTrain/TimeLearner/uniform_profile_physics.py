"""Audit a fixed uniform storage profile across native learning/growth.

Only morphology, synapse counts and positive individual Rs may change here.
This is data consistency, never native execution, a training certificate or
support for a heterogeneous starting profile.
"""
import re
from .domain_evidence import _property
from .model_identity import canonical_model_sha256
from .native_evidence import require

CHANNEL_FIELDS=('Capacity','Resistance','RestingResistance','FBResistance','Type')
SYNAPSE_FIELDS=('SecretionTC','DissociationTC','TypicalPulseDuration','PulseAmplitude',
                'UsePulseSignal','UsePresynapticInhibition','InhibitionCoeff','Type')
MEMBRANE_FIELDS=('FeedbackGain','UseAveragePotential')
BODY=re.compile(r'\$\.(?:Soma\d+|Dendrite\d+_\d+)')


def _value(node, name):
    prop=node['parameters'][name];require(prop['binding'] is False,'uniform_profile_bound_parameter')
    data=prop['data']
    if data['type'] in ('signed_integer','unsigned_integer'):
        text=data['value'];require(type(text) is str and re.fullmatch(r'-?(?:0|[1-9][0-9]*)',text),
                                  'uniform_profile_invalid_integer')
        value=int(text);require(data['type']!='unsigned_integer' or value>=0,'uniform_profile_invalid_integer')
        return value
    return _property(node,name)


def audit_uniform_profile(initial, final):
    def nodes(identity):
        require(identity['valid'] is True and identity['diagnostics']==[] and
                identity['sha256']==canonical_model_sha256(identity['model']),
                'uniform_profile_identity_invalid')
        result={n['path']:n for n in identity['model']['nodes']}
        require(len(result)==len(identity['model']['nodes']), 'uniform_profile_duplicate_path')
        return result
    before,after=nodes(initial),nodes(final)
    require('$.Soma1' in before and before['$']['class']==after['$']['class'],
            'uniform_profile_root_changed')
    require(_value(before['$'],'UseElementDefaults') is False and
            _value(after['$'],'UseElementDefaults') is False, 'uniform_profile_parent_defaults_enabled')
    mutable_root={'NumDendriteMembranePartsVec','TrainingDendIndexes','TrainingSynapsisNum'}
    def fixed_root(node):
        return {k:v for k,v in node['parameters'].items() if k not in mutable_root}
    require(fixed_root(before['
    require(all(n['frequency_hz']==rate for n in [*before.values(),*after.values()]),
            'uniform_profile_frequency_changed')
    def fixed(ns):
        return {p:n for p,n in ns.items() if p!='$' and not BODY.fullmatch(p) and
                not any(BODY.fullmatch(p[:i]) for i,c in enumerate(p) if c=='.')}
    require(fixed(before)==fixed(after), 'uniform_profile_fixed_component_changed')
    require({p for p in before if re.fullmatch(r'\$\.Soma\d+',p)}==
            {p for p in after if re.fullmatch(r'\$\.Soma\d+',p)}, 'uniform_profile_somas_changed')
    def fields(actual,expected,keys):
        require(actual['class']==expected['class'], 'uniform_profile_child_class_changed')
        for key in keys:
            require(_value(actual,key)==_value(expected,key), 'uniform_profile_physics_changed:'+key)
    counts={}
    for label,ns in (('initial',before),('final',after)):
        checked=0
        for path,membrane in ns.items():
            if not BODY.fullmatch(path):continue
            fields(membrane,before['$.Soma1'],MEMBRANE_FIELDS)
            expected_children=set()
            for role in ('Exc','Inh'):
                ch=path+'.'+role+'Channel';require(ch in ns,'uniform_profile_channel_missing')
                fields(ns[ch],before['$.Soma1.'+role+'Channel'],CHANNEL_FIELDS)
                expected_children.add(ch)
                bank=[p for p in ns if re.fullmatch(re.escape(path)+r'\.'+role+r'Synapse\d+',p)]
                number=_value(membrane,'Num'+('Excitatory' if role=='Exc' else 'Inhibitory')+'Synapses')
                require(type(number) is int and number>=0 and len(bank)==number,
                        'uniform_profile_synapse_inventory_changed')
                require(set(bank)=={path+'.'+role+'Synapse'+str(i+1) for i in range(int(number))},
                        'uniform_profile_synapse_names_changed')
                for p in bank:
                    fields(ns[p],before['$.Soma1.'+role+'Synapse1'],SYNAPSE_FIELDS)
                    require(_value(ns[p],'Resistance')>0, 'uniform_profile_nonpositive_learned_resistance')
                expected_children.update(bank)
            actual_children={p for p in ns if p.startswith(path+'.')}
            require(actual_children==expected_children,'uniform_profile_unexpected_body_child')
            checked+=1
        require(checked>0,'uniform_profile_body_missing');counts[label]=checked
    def lt_links(model):
        return sorted((b['source'],b['target'],b['kind']) for b in model['bindings']
                      if b['target']=='$.LTZone:Inputs' or b['source']=='$.LTZone:Output')
    require(lt_links(initial['model'])==lt_links(final['model']), 'uniform_profile_lt_links_changed')
    return dict(kind='timelearner_uniform_profile_physics_audit',schema_version=1,
        membranes_checked=counts,frequency_hz=rate,uniform_physics_preserved=True,
        positive_individual_resistances_allowed=True,threshold_and_feedback_preserved=True,
        native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
])==fixed_root(after['
    require(all(n['frequency_hz']==rate for n in [*before.values(),*after.values()]),
            'uniform_profile_frequency_changed')
    def fixed(ns):
        return {p:n for p,n in ns.items() if p!='$' and not BODY.fullmatch(p) and
                not any(BODY.fullmatch(p[:i]) for i,c in enumerate(p) if c=='.')}
    require(fixed(before)==fixed(after), 'uniform_profile_fixed_component_changed')
    require({p for p in before if re.fullmatch(r'\$\.Soma\d+',p)}==
            {p for p in after if re.fullmatch(r'\$\.Soma\d+',p)}, 'uniform_profile_somas_changed')
    def fields(actual,expected,keys):
        require(actual['class']==expected['class'], 'uniform_profile_child_class_changed')
        for key in keys:
            require(_value(actual,key)==_value(expected,key), 'uniform_profile_physics_changed:'+key)
    counts={}
    for label,ns in (('initial',before),('final',after)):
        checked=0
        for path,membrane in ns.items():
            if not BODY.fullmatch(path):continue
            fields(membrane,before['$.Soma1'],MEMBRANE_FIELDS)
            expected_children=set()
            for role in ('Exc','Inh'):
                ch=path+'.'+role+'Channel';require(ch in ns,'uniform_profile_channel_missing')
                fields(ns[ch],before['$.Soma1.'+role+'Channel'],CHANNEL_FIELDS)
                expected_children.add(ch)
                bank=[p for p in ns if re.fullmatch(re.escape(path)+r'\.'+role+r'Synapse\d+',p)]
                number=_value(membrane,'Num'+('Excitatory' if role=='Exc' else 'Inhibitory')+'Synapses')
                require(type(number) is int and number>=0 and len(bank)==number,
                        'uniform_profile_synapse_inventory_changed')
                require(set(bank)=={path+'.'+role+'Synapse'+str(i+1) for i in range(int(number))},
                        'uniform_profile_synapse_names_changed')
                for p in bank:
                    fields(ns[p],before['$.Soma1.'+role+'Synapse1'],SYNAPSE_FIELDS)
                    require(_value(ns[p],'Resistance')>0, 'uniform_profile_nonpositive_learned_resistance')
                expected_children.update(bank)
            actual_children={p for p in ns if p.startswith(path+'.')}
            require(actual_children==expected_children,'uniform_profile_unexpected_body_child')
            checked+=1
        require(checked>0,'uniform_profile_body_missing');counts[label]=checked
    def lt_links(model):
        return sorted((b['source'],b['target'],b['kind']) for b in model['bindings']
                      if b['target']=='$.LTZone:Inputs' or b['source']=='$.LTZone:Output')
    require(lt_links(initial['model'])==lt_links(final['model']), 'uniform_profile_lt_links_changed')
    return dict(kind='timelearner_uniform_profile_physics_audit',schema_version=1,
        membranes_checked=counts,frequency_hz=rate,uniform_physics_preserved=True,
        positive_individual_resistances_allowed=True,threshold_and_feedback_preserved=True,
        native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
]),
            'uniform_profile_root_spec_changed')
    rate=before['
    require(all(n['frequency_hz']==rate for n in [*before.values(),*after.values()]),
            'uniform_profile_frequency_changed')
    def fixed(ns):
        return {p:n for p,n in ns.items() if p!='$' and not BODY.fullmatch(p) and
                not any(BODY.fullmatch(p[:i]) for i,c in enumerate(p) if c=='.')}
    require(fixed(before)==fixed(after), 'uniform_profile_fixed_component_changed')
    require({p for p in before if re.fullmatch(r'\$\.Soma\d+',p)}==
            {p for p in after if re.fullmatch(r'\$\.Soma\d+',p)}, 'uniform_profile_somas_changed')
    def fields(actual,expected,keys):
        require(actual['class']==expected['class'], 'uniform_profile_child_class_changed')
        for key in keys:
            require(_value(actual,key)==_value(expected,key), 'uniform_profile_physics_changed:'+key)
    counts={}
    for label,ns in (('initial',before),('final',after)):
        checked=0
        for path,membrane in ns.items():
            if not BODY.fullmatch(path):continue
            fields(membrane,before['$.Soma1'],MEMBRANE_FIELDS)
            expected_children=set()
            for role in ('Exc','Inh'):
                ch=path+'.'+role+'Channel';require(ch in ns,'uniform_profile_channel_missing')
                fields(ns[ch],before['$.Soma1.'+role+'Channel'],CHANNEL_FIELDS)
                expected_children.add(ch)
                bank=[p for p in ns if re.fullmatch(re.escape(path)+r'\.'+role+r'Synapse\d+',p)]
                number=_value(membrane,'Num'+('Excitatory' if role=='Exc' else 'Inhibitory')+'Synapses')
                require(type(number) is int and number>=0 and len(bank)==number,
                        'uniform_profile_synapse_inventory_changed')
                require(set(bank)=={path+'.'+role+'Synapse'+str(i+1) for i in range(int(number))},
                        'uniform_profile_synapse_names_changed')
                for p in bank:
                    fields(ns[p],before['$.Soma1.'+role+'Synapse1'],SYNAPSE_FIELDS)
                    require(_value(ns[p],'Resistance')>0, 'uniform_profile_nonpositive_learned_resistance')
                expected_children.update(bank)
            actual_children={p for p in ns if p.startswith(path+'.')}
            require(actual_children==expected_children,'uniform_profile_unexpected_body_child')
            checked+=1
        require(checked>0,'uniform_profile_body_missing');counts[label]=checked
    def lt_links(model):
        return sorted((b['source'],b['target'],b['kind']) for b in model['bindings']
                      if b['target']=='$.LTZone:Inputs' or b['source']=='$.LTZone:Output')
    require(lt_links(initial['model'])==lt_links(final['model']), 'uniform_profile_lt_links_changed')
    return dict(kind='timelearner_uniform_profile_physics_audit',schema_version=1,
        membranes_checked=counts,frequency_hz=rate,uniform_physics_preserved=True,
        positive_individual_resistances_allowed=True,threshold_and_feedback_preserved=True,
        native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
]['frequency_hz']
    require(all(n['frequency_hz']==rate for n in [*before.values(),*after.values()]),
            'uniform_profile_frequency_changed')
    def fixed(ns):
        return {p:n for p,n in ns.items() if p!='$' and not BODY.fullmatch(p) and
                not any(BODY.fullmatch(p[:i]) for i,c in enumerate(p) if c=='.')}
    require(fixed(before)==fixed(after), 'uniform_profile_fixed_component_changed')
    require({p for p in before if re.fullmatch(r'\$\.Soma\d+',p)}==
            {p for p in after if re.fullmatch(r'\$\.Soma\d+',p)}, 'uniform_profile_somas_changed')
    def fields(actual,expected,keys):
        require(actual['class']==expected['class'], 'uniform_profile_child_class_changed')
        for key in keys:
            require(_value(actual,key)==_value(expected,key), 'uniform_profile_physics_changed:'+key)
    counts={}
    for label,ns in (('initial',before),('final',after)):
        checked=0
        for path,membrane in ns.items():
            if not BODY.fullmatch(path):continue
            fields(membrane,before['$.Soma1'],MEMBRANE_FIELDS)
            expected_children=set()
            for role in ('Exc','Inh'):
                ch=path+'.'+role+'Channel';require(ch in ns,'uniform_profile_channel_missing')
                fields(ns[ch],before['$.Soma1.'+role+'Channel'],CHANNEL_FIELDS)
                expected_children.add(ch)
                bank=[p for p in ns if re.fullmatch(re.escape(path)+r'\.'+role+r'Synapse\d+',p)]
                number=_value(membrane,'Num'+('Excitatory' if role=='Exc' else 'Inhibitory')+'Synapses')
                require(type(number) is int and number>=0 and len(bank)==number,
                        'uniform_profile_synapse_inventory_changed')
                require(set(bank)=={path+'.'+role+'Synapse'+str(i+1) for i in range(int(number))},
                        'uniform_profile_synapse_names_changed')
                for p in bank:
                    fields(ns[p],before['$.Soma1.'+role+'Synapse1'],SYNAPSE_FIELDS)
                    require(_value(ns[p],'Resistance')>0, 'uniform_profile_nonpositive_learned_resistance')
                expected_children.update(bank)
            actual_children={p for p in ns if p.startswith(path+'.')}
            require(actual_children==expected_children,'uniform_profile_unexpected_body_child')
            checked+=1
        require(checked>0,'uniform_profile_body_missing');counts[label]=checked
    def lt_links(model):
        return sorted((b['source'],b['target'],b['kind']) for b in model['bindings']
                      if b['target']=='$.LTZone:Inputs' or b['source']=='$.LTZone:Output')
    require(lt_links(initial['model'])==lt_links(final['model']), 'uniform_profile_lt_links_changed')
    return dict(kind='timelearner_uniform_profile_physics_audit',schema_version=1,
        membranes_checked=counts,frequency_hz=rate,uniform_physics_preserved=True,
        positive_individual_resistances_allowed=True,threshold_and_feedback_preserved=True,
        native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
