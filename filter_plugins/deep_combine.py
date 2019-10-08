from ansible import errors
from collections.abc import MutableMapping
import ast

class FilterModule(object):
    ''' A filter to deep-merge two dicts. '''
    def filters(self):
        return {
            'deep_combine': self.deep_combine
        }

    def deep_combine(self, d1, d2):
        try:
            # If d1 or d2 are not dicts, try to convert them to dicts
            if type(d1) is not dict: d1 = ast.literal_eval(str(d1))
            if type(d2) is not dict: d2 = ast.literal_eval(str(d2))
        except Exception as e:
            raise errors.AnsibleFilterError(
                'deep_combine plugin error (dict conversion fail): {0}, '
                'dictA={1}, dictB={2}'.format(str(e), str(d1), str(d2))
            )
        if type(d1) is not dict: self._not_dict(d1)
        if type(d2) is not dict: self._not_dict(d2)

        # if not d1: return d2 # If one of the dicts is empty, simply return the other 
        # if not d2: return d1
        try:
            merged_dict = self._recursive_merge(d1, d2)
            # raise errors.AnsibleFilterError(
            #     'deep_combine test error: {0}'.format(type(merged_dict))
            # )
        except Exception as e:
            raise errors.AnsibleFilterError(
                'deep_combine plugin error: {0}, dictA({1})={2},'
                'dictB{3}={4}'.format(
                    str(e),
                    type(d1),
                    str(d1),
                    type(d2),
                    str(d2),
                )
            )
        return merged_dict

    def _recursive_merge(self, d1, d2):
        '''
        Update two dicts of dicts recursively, 
        if either mapping has leaves that are non-dicts, 
        the second's leaf overwrites the first's.
        '''
        for k, v in d1.items(): # in Python 2, use .iteritems()!
            if k in d2:
                # this next check is the only difference!
                if all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                    d2[k] = self._recursive_merge(v, d2[k])
                # we could further check types and merge as appropriate here.
        d3 = d1.copy()
        d3.update(d2)
        return d3

    def _not_dict(self, d):
        raise errors.AnsibleFilterError(
            'deep_combine plugin error - type({0}) is not dict. Data = {1}'.format(
                type(d),
                d
            )
        )
