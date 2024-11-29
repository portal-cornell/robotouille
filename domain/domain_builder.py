from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.action import Action
from backend.special_effects.delayed_effect import DelayedEffect
from backend.special_effects.repetitive_effect import RepetitiveEffect
from backend.special_effects.conditional_effect import ConditionalEffect
from backend.special_effects.creation_effect import CreationEffect
from backend.special_effects.deletion_effect import DeletionEffect
from backend.special_effects.parametrized_deletion_effect import ParametrizedDeletionEffect


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

def _build_pred_list(defn, param_objs, predicate_dict):
    """
    This function builds a list of predicates from a JSON input. This is used 
    in building actions and special effects, where their preconditions, 
    immediate effects, or conditions are defined as a list of predicates.
    
    Args:
        defn (List[Dictionary[str, any]]): A list of predicate definitions.
        param_objs (Dictionary[str, Object]): A dictionary whose keys are
            parameter names and the values are placeholder objects. 
        predicate_dict (Dictionary[str, Predicate]): The predicate dictionary.

    Returns:
        predicates (Dictionary[Predicate, bool]): A predicate dictionary built
            based on the json input. 

    Side Effects:
        - Updates 'param_objs' in-place with parameter objects.
    """
    precons_or_effects = {}

    for precon_or_effect in defn:
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

def _build_special_effects(defn, param_objs, predicate_dict):
    """
    This function builds special effects. 

    Args:
        defn (List[Dictionary[str, any]]): A list of special effect definitions.
        param_objs (Dictionary[str, Object]): A dictionary whose keys are
            parameter names and the values are placeholder objects. 
        predicate_dict (Dictionary[str, Predicate]): The predicate dictionary.

    Returns:
        special_effects (List[SpecialEffect]): The special effects of the action.

    Side Effects:
        - Updates 'param_objs' in-place with parameter objects.
    """
    special_effects = []

    for special_effect in defn:
        param_name = special_effect["param"]
        param_obj = param_objs[param_name]
        effects = _build_pred_list(
            special_effect["fx"], param_objs, predicate_dict)
        nested_sfx = _build_special_effects(special_effect["sfx"], param_objs, predicate_dict)
        if special_effect["type"] == "delayed":
            # TODO (lsuyean): The values for goal repetitions/time should be decided by the problem json
            sfx = DelayedEffect(param_obj, effects, nested_sfx)
        elif special_effect["type"] == "repetitive":
            sfx = RepetitiveEffect(param_obj, effects, nested_sfx)
        elif special_effect["type"] == "conditional":
            conditions = _build_pred_list(
                special_effect["conditions"], param_objs, predicate_dict)
            sfx = ConditionalEffect(param_obj, effects, nested_sfx, conditions)
        elif special_effect["type"] == "creation":
            created_obj_attrs = special_effect["created_obj"]
            created_obj_name = created_obj_attrs["name"]
            created_obj_type = created_obj_attrs["type"]
            created_obj_param = created_obj_attrs["param"]
            created_obj = Object(created_obj_name, created_obj_type)
            sfx = CreationEffect(param_obj, (created_obj_param, created_obj), effects, nested_sfx)        
        elif special_effect["type"] == "deletion":
            sfx = DeletionEffect(param_obj, effects, nested_sfx)    
        elif special_effect["type"] == "parametrized_deletion":
            predicate = predicate_dict[special_effect["predicate"]]
            sfx = ParametrizedDeletionEffect(param_obj, predicate, effects, nested_sfx)
        special_effects.append(sfx)

    return special_effects

def _build_action_defs(input_json, predicate_defs, action_type):
    """
    This function builds action definitions from a JSON input.

    Args:
        input_json (str): The JSON input.
        predicate_defs (List[Predicate]): The predicate definitions.
        action_type (str): Whether the action is a player action or an NPC action.

    Returns:
        action_defs (List[Action]): The action definitions.
    """
    predicate_dict = {pred.name: pred for pred in predicate_defs}

    action_defs = []

    param_objs = {}

    for action in input_json[action_type]:
        name = action["name"]
        precons = _build_pred_list(
            action["precons"], param_objs, predicate_dict)
        immediate_effects = _build_pred_list(
            action["immediate_fx"], param_objs, predicate_dict)
        special_effects = _build_special_effects(
            action["sfx"], param_objs, predicate_dict)
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

    action_defs = _build_action_defs(input_json, predicate_defs, "player_action_defs")

    npc_action_defs = _build_action_defs(input_json, predicate_defs, "npc_action_defs")

    domain = Domain().initialize(name, object_types, predicate_defs, action_defs, npc_action_defs)

    return domain
        
