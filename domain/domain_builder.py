from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.action import Action
from backend.special_effects.delayed_effect import DelayedEffect
from backend.special_effects.repetitive_effect import RepetitiveEffect
from backend.special_effects.conditional_effect import ConditionalEffect


def _build_predicate_defs(input_json):
    """
    This function builds predicate definitions from a JSON input.

    Args:
        input_json (str): The JSON input.

    Returns:
        predicate_defs (List[Predicate]): The predicate definitions.
    """
    predicate_defs = []

    for pred in input_json["predicate_defs"]:
        name = pred["name"]
        param_types = pred["param_types"]
        predicate_defs.append(Predicate().initialize(name, param_types))

    return predicate_defs

def _build_precons_or_effects(precon_or_effect_key, param_objs, action, predicate_dict):
    """
    This function builds the preconditions or immediate effects of an action.
    
    Args:
        domain_dict (Dictionary): The domain dictionary.
        precon_or_effect_key (str): The key for the preconditions or immediate
            effects in the domain dictionary.
        param_objs (Dictionary[str, Object]): The parameter objects to prevent 
            unnecessary object creation.
        action (Dictionary): The action to build the preconditions or immediate
            effects from.
        predicate_dict (Dictionary[str, Predicate]): The predicate dictionary.

    Returns:
        precons_or_effects (Dictionary[Predicate, bool]): The preconditions or
            immediate effects of the action.
        param_objs (Dictionary[str, Object]): The updated parameter objects.
    """
    precons_or_effects = {}

    for precon_or_effect in action[precon_or_effect_key]:
        pred = predicate_dict[precon_or_effect["predicate"]]
        params = []
        for param in precon_or_effect["params"]:
            if param not in param_objs.keys():
                type = pred.types[precon_or_effect["params"].index(param)]
                param_objs[param] = Object(param, type)
            params.append(param_objs[param])
        new_pred = Predicate().initialize(pred.name, pred.types, params)
        precons_or_effects[new_pred] = precon_or_effect["is_true"]

    return precons_or_effects, param_objs

def _build_special_effects(action, param_objs, predicate_dict):
    """
    This function builds the special effects of an action.

    Args:
        action (Dictionary): The action to build the special effects from.
        param_objs (Dictionary[str, Object]): The parameter objects to prevent 
            unnecessary object creation.
        predicate_dict (Dictionary[str, Predicate]): The predicate dictionary.

    Returns:
        special_effects (List[SpecialEffect]): The special effects of the action.
        param_objs (Dictionary[str, Object]): The updated parameter objects.
    """
    special_effects = []

    for special_effect in action["special_fx"]:
        param_name = special_effect["param"]
        param_obj = param_objs[param_name]
        effects = {}
        for effect in special_effect["fx"]:
            pred = predicate_dict[effect["predicate"]]
            params = []
            for param in effect["params"]:
                if param not in param_objs.keys():
                    type = pred.types[effect["params"].index(param)]
                    param_objs[param] = Object(param, type)
                params.append(param_objs[param])
            new_pred = Predicate().initialize(pred.name, pred.types, params)
            effects[new_pred] = effect["is_true"]
        if special_effect["type"] == "delayed":
            sfx = DelayedEffect(param_obj, effects, False, 4)
        elif special_effect["type"] == "repetitive":
            sfx = RepetitiveEffect(param_obj, effects, False, 3)
        elif special_effect["type"] == "conditional":
            conditions = {}
            for condition in special_effect["conditions"]:
                pred = predicate_dict[condition["predicate"]]
                params = []
                for param in condition["params"]:
                    if param not in param_objs.keys():
                        type = pred.types[condition["params"].index(param)]
                        param_objs[param] = Object(param, type)
                    params.append(param_objs[param])
                new_pred = Predicate().initialize(pred.name, pred.types, params)
                conditions[new_pred] = condition["is_true"]
            sfx = ConditionalEffect(param_obj, effects, False, conditions)
        special_effects.append(sfx)

    return special_effects, param_objs

def _build_action_defs(input_json, predicate_defs):
    """
    This function builds action definitions from a JSON input.

    Args:
        input_json (str): The JSON input.
        predicate_defs (List[Predicate]): The predicate definitions.

    Returns:
        action_defs (List[Action]): The action definitions.
        param_objs (Dictionary[str, Object]): The parameter objects to prevent 
            unnecessary object creation.
    """
    predicate_dict = {pred.name: pred for pred in predicate_defs}

    action_defs = []

    param_objs = {}

    for action in input_json["action_defs"]:
        name = action["name"]
        precons, param_objs = _build_precons_or_effects(
            "precons", param_objs, action, predicate_dict)
        immediate_effects, param_objs = _build_precons_or_effects(
            "immediate_fx", param_objs, action, predicate_dict)
        special_effects, param_objs = _build_special_effects(
            action, param_objs, predicate_dict)
        action_def = Action(name, precons, immediate_effects, special_effects)
        action_defs.append(action_def)

    return action_defs, param_objs
        
def build_domain(input_json):
    """
    This function builds a domain object from a JSON input.

    Args:
        input_json (str): The JSON input.

    Returns:
        domain (Domain): The domain object.
        param_objs (Dictionary[str, Object]): The parameter objects to prevent 
            unnecessary object creation.
    """
    name = input_json["name"]

    object_types = input_json["object_types"]

    predicate_defs = _build_predicate_defs(input_json)

    action_defs, param_objs = _build_action_defs(input_json, predicate_defs)

    domain = Domain().initialize(name, object_types, predicate_defs, action_defs)

    return domain, param_objs
        
