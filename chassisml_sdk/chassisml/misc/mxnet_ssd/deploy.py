from __future__ import print_function
import chassisml.misc.mxnet_ssd.tools.find_mxnet
import mxnet as mx
import os
import importlib
import sys
from chassisml.misc.mxnet_ssd.symbol.symbol_factory import get_symbol

def convert_to_deployable(network,data_shape,num_classes,nms_thresh,prefix,epoch,force_nms=True,nms_topk=400):
    net = get_symbol(network, data_shape,
        num_classes=num_classes, nms_thresh=nms_thresh,
        force_suppress=force_nms, nms_topk=nms_topk)
    if prefix.endswith('_'):
        prefix = prefix + args.network + '_' + str(args.data_shape)
    else:
        prefix = prefix
    _, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
    # new name
    tmp = prefix.rsplit('/', 1)
    save_prefix = '/deploy_'.join(tmp)
    mx.model.save_checkpoint(save_prefix, epoch, net, arg_params, aux_params)

    return "{}-{:04d}.params".format(save_prefix, epoch),"{}-symbol.json".format(save_prefix)