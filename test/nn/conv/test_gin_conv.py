from itertools import repeat

import torch
from torch.nn import Sequential as Seq, Linear as Lin, ReLU
from torch_geometric.nn import GINConv, GINEConv


def test_gin_conv():
    in_channels, out_channels = (16, 32)
    edge_index = torch.tensor([[0, 0, 0, 1, 2, 3], [1, 2, 3, 0, 0, 0]])
    num_nodes = edge_index.max().item() + 1
    x = torch.randn((num_nodes, in_channels))

    nn = Seq(Lin(in_channels, 32), ReLU(), Lin(32, out_channels))
    conv = GINConv(nn, train_eps=True)
    assert conv.__repr__() == (
        'GINConv(nn=Sequential(\n'
        '  (0): Linear(in_features=16, out_features=32, bias=True)\n'
        '  (1): ReLU()\n'
        '  (2): Linear(in_features=32, out_features=32, bias=True)\n'
        '))')
    out = conv(x, edge_index)
    assert out.size() == (num_nodes, out_channels)

    jit_conv = conv.jittable(x=x, edge_index=edge_index)
    jit_conv = torch.jit.script(jit_conv)
    assert jit_conv(x, edge_index).tolist() == out.tolist()


def test_gine_conv():
    in_channels, out_channels = (16, 32)
    edge_index = torch.tensor([[0, 0, 0, 1, 2, 3], [1, 2, 3, 0, 0, 0]])
    num_nodes = edge_index.max().item() + 1
    x = torch.randn((num_nodes, in_channels))
    edge_attr = torch.randn((edge_index.size(1), in_channels))

    nn = Seq(Lin(in_channels, 32), ReLU(), Lin(32, out_channels))
    conv = GINEConv(nn, train_eps=True)
    assert conv.__repr__() == (
        'GINEConv(nn=Sequential(\n'
        '  (0): Linear(in_features=16, out_features=32, bias=True)\n'
        '  (1): ReLU()\n'
        '  (2): Linear(in_features=32, out_features=32, bias=True)\n'
        '))')
    out = conv(x, edge_index, edge_attr)
    assert out.size() == (num_nodes, out_channels)

    jit_conv = conv.jittable(x=x, edge_index=edge_index, edge_attr=edge_attr)
    jit_conv = torch.jit.script(jit_conv)
    assert jit_conv(x, edge_index, edge_attr).tolist() == out.tolist()


def test_gin_conv_on_regular_graph():
    edge_index = torch.tensor([[0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
                               [1, 5, 0, 2, 1, 3, 2, 4, 3, 5, 0, 4]])
    x = torch.ones(6, 1)
    conv = GINConv(Seq(Lin(1, 8), ReLU(), Lin(8, 8)))

    out = conv(x, edge_index)
    for i in range(8):
        assert out[:, i].tolist() == list(repeat(out[0, i].item(), 6))
