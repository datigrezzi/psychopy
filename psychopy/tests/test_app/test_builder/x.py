import sys, os

import wx
tmpApp = wx.PySimpleApp()
from psychopy.app import builder
from psychopy.app.builder.components import getAllComponents

# usage: generate or compare all Component.param settings & options

# motivation: catch deviations introduced during refactoring

# use --out to generate a new target file (sent to sys.stdout, so redirect to a file)
# or compare against a prior run (x.out.master.de55d49)

# current target file is x.out.master.de55d49, which is the output of this script --out
# as run on upstream/master branch @ de55d49, with edits to fix known-good changes
# introduced by refactoring: nVertices 4, Patch interpolation 'linear'

# should not need a wx.App with fetchIcons=False
try:
    allComp = getAllComponents(fetchIcons=False)
except:
    import wx
    tmpApp = wx.PySimpleApp()
    try: from psychopy.app import localization
    except: pass  # not needed if can't import it
    allComp = getAllComponents(fetchIcons=False)

exp = builder.experiment.Experiment()

if not '--out' in sys.argv:
    target = open('x.out.master.de55d49', 'rU').read()
    targetLines = target.splitlines()
    targetTag = {}
    for line in targetLines:
        try:
            t, val = line.split(':',1)
            targetTag[t] = val
        except ValueError:
            # need more than one value to unpack; this is a weak way to
            # handle multi-line default values, eg TextComponent.text.default
            targetTag[t] += '\n' + line  # previous t value

param = builder.experiment.Param('', '')  # want its namespace
ignore = ['__doc__', '__init__', '__module__', '__str__']
if not '--out' in sys.argv:
    # these are for display only (cosmetic) but no harm in gathering initially:
    ignore += ['hint',
               'label',  # comment-out to not ignore labels when checking
               'categ'
               ]
fields = set(dir(param)).difference(ignore)

mismatches = []
for compName in sorted(allComp):
    comp = allComp[compName](parentName='x', exp=exp)

    order = '%s.order: %s' % (compName, eval("comp.order"))
    out = [order]
    if '--out' in sys.argv:
        print order.encode('utf8')
    elif not order+'\n' in target:
        tag = order.split(':',1)[0]
        try:
            err = order + ' <== ' + targetTag[tag]
        except IndexError: # missing
            err = order + ' <==> NEW (no matching param in original)'
        print err.encode('utf8')
        mismatches.append(err)
    for parName in comp.params.keys():
        # default is what you get from param.__str__, which returns its value
        default = '%s.%s.default: %s' % (compName, parName, comp.params[parName])
        out.append(default)
        lineFields = []
        for field in fields:
            if parName == 'name' and field == 'updates':
                continue
                # ignore b/c never want to change the name *during a running experiment*
                # the default name.updates value varies across existing components
            f = '%s.%s.%s: %s' % (compName, parName, field, eval("comp.params[parName].%s" % field))
            lineFields.append(f)

        for line in [default] + lineFields:
            if '--out' in sys.argv:
                print line.encode('utf8')
            elif not line+'\n' in target:
                # mismatch, so report on the tag from orig file
                # match checks tag + multi-line, because line is multi-line and target is whole file
                tag = line.split(':',1)[0]
                try:
                    err = line + ' <== ' + targetTag[tag]
                except KeyError: # missing
                    err = line + ' <==> NEW (no matching param in original)'
                print err.encode('utf8')
                mismatches.append(err)

#return mismatches
