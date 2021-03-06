## Script (Python) "prepare_slots"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=generate a mapping based on the context slots
##
#prepare a structure that makes it conveient to determine
#if we want to use-macro or render the path expression.
#the values for the dictioanries is a list of tuples
#that are path expressions and the second value is a
#1 for use-macro
#0 for render path expression

slots={ 'left':[],
        'right':[],
        'document_actions':[] }

left_slots=getattr(context,'left_slots', [])
right_slots=getattr(context,'right_slots', [])
document_action_slots=getattr(context,'document_action_slots', [])

#check if the *_slots attributes are callable so that they can be overridden
#by methods or python scripts

if callable(left_slots):
    left_slots=left_slots()

if callable(right_slots):
    right_slots=right_slots()

if callable(document_action_slots):
    document_action_slots=document_action_slots()

for slot in left_slots:
    if not slot: continue
    if slot.find('/macros/')!=-1:
        slots['left'].append( (slot, 1) )
    else:
        slots['left'].append( (slot, 0) )

for slot in right_slots:
    if not slot: continue
    if slot.find('/macros/')!=-1:
        slots['right'].append( (slot, 1) )
    else:
        slots['right'].append( (slot, 0) )

for slot in document_action_slots:
    if not slot: continue
    if slot.find('/macros/')!=-1:
        slots['document_actions'].append( (slot, 1) )
    else:
        slots['document_actions'].append( (slot, 0) )

return slots
