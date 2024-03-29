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

def _build_pred_list(key, param_objs, dict, predicate_dict):
    """
    This function builds a list of predicates from a JSON input. This is used 
    in building actions and special effects, where their preconditions, 
    immediate effects, or conditions are defined as a list of predicates.
    
    Args:
        key (str): The key for the list or predicates being built 
            (e.g. "precons").
        param_objs (Dictionary[str, Object]): A dictionary whose keys are
            parameter names and the values are placeholder objects. 
        dict (Dictionary): The dictionary containing the predicates to be built. 
        predicate_dict (Dictionary[str, Predicate]): The predicate dictionary.

    Returns:
        precons_or_effects (Dictionary[Predicate, bool]): The preconditions or
            immediate effects of the action.

    Side Effects:
        - Updates 'param_objs' in-place with parameter objects.
    """
    precons_or_effects = {}

    for precon_or_effect in dict[key]:
        pred = predicate_dict[precon_or_effect["predicate"]]
        params = []
        for i, param in enumerate(precon_or_effect["params"]):
            if param not in param_objs.keys():
                type = pred.types[i]
                param_objs[param] = Object(param, type)
            params.append(param_objs[param])
        new_pred = Predicate().initialize(pred.name, pred.types, params)
        precons_or_effects[new_pred] = precon_or_effect["is_true"]

    return precons_or_effects

def _build_special_effects(action, param_objs, predicate_dict):
    """
    This function builds the special effects of an action.

    Args:
        action (Dictionary): The action to build the special effects from.
        param_objs (Dictionary[str, Object]): A dictionary whose keys are
            parameter names and the values are placeholder objects. 
        predicate_dict (Dictionary[str, Predicate]): The predicate dictionary.

    Returns:
        special_effects (List[SpecialEffect]): The special effects of the action.

    Side Effects:
        - Updates 'param_objs' in-place with parameter objects.
    """
    special_effects = []

    for special_effect in action["special_fx"]:
        param_name = special_effect["param"]
        param_obj = param_objs[param_name]
        effects = _build_pred_list(
            "fx", param_objs, special_effect, predicate_dict)
        if special_effect["type"] == "delayed":
            # TODO: The values for goal repetitions/time should be decided by the problem json
            sfx = DelayedEffect(param_obj, effects, False)
        elif special_effect["type"] == "repetitive":
            sfx = RepetitiveEffect(param_obj, effects, False)
        elif special_effect["type"] == "conditional":
            conditions = _build_pred_list(
                "conditions", param_objs, special_effect, predicate_dict)
            sfx = ConditionalEffect(param_obj, effects, False, conditions)
        special_effects.append(sfx)

    return special_effects

def _build_action_defs(input_json, predicate_defs):
    """
    This function builds action definitions from a JSON input.

    Args:
        input_json (str): The JSON input.
        predicate_defs (List[Predicate]): The predicate definitions.

    Returns:
        action_defs (List[Action]): The action definitions.
    """
    predicate_dict = {pred.name: pred for pred in predicate_defs}

    action_defs = []

    param_objs = {}

    for action in input_json["action_defs"]:
        name = action["name"]
        precons = _build_pred_list(
            "precons", param_objs, action, predicate_dict)
        immediate_effects = _build_pred_list(
            "immediate_fx", param_objs, action, predicate_dict)
        special_effects = _build_special_effects(
            action, param_objs, predicate_dict)
        action_def = Action(name, precons, immediate_effects, special_effects)
        action_defs.append(action_def)

    return action_defs
        
def build_domain(input_json):
    """
    This function builds a domain object from a JSON input.

    Args:
        input_json (str): The JSON input.

    Returns:
        domain (Domain): The domain object.
    """
    name = input_json["name"]

    object_types = input_json["object_types"]

    predicate_defs = _build_predicate_defs(input_json)

    action_defs = _build_action_defs(input_json, predicate_defs)

    domain = Domain().initialize(name, object_types, predicate_defs, action_defs)

    return domain
        
