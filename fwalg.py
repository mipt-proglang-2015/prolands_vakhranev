__author__ = 'Anton'

import sys
import time
import xml
from xml.etree import ElementTree
import sys
import fwalg

CONST_RESISTOR_TAG = "resistor"
CONST_CAPATOR_TAG = "capactor"
CONST_DIOD_TAG = "diode"
CONST_NODE_TAG = "net"

CONST_NET_FROM_ATR = "net_from"
CONST_NET_TO_ATR = "net_to"
CONST_RESISTANCE_ATR = "resistance"
CONST_REVERSE_RESISTANCE_ATR = "reverse_resistance"
CONST_ID_ATR = "id"


def form_nodes_list(tree):
    nodes = tree.findall(CONST_NODE_TAG)
    nodes_list = []
    for node in nodes:
        nodes_list.append(int(node.attrib[CONST_ID_ATR]))
    nodes_list.sort()
    return nodes_list

def form_edges_list(tree):
    resistors = tree.findall(CONST_RESISTOR_TAG)
    capactors = tree.findall(CONST_CAPATOR_TAG)
    diodes = tree.findall(CONST_DIOD_TAG)
    edges_list = []

    for resistor in resistors:
        from_net = int(resistor.attrib[CONST_NET_FROM_ATR])
        to_net = int(resistor.attrib[CONST_NET_TO_ATR])
        edges_list.append([from_net, to_net, float(resistor.attrib[CONST_RESISTANCE_ATR])])
        edges_list.append([to_net, from_net, float(resistor.attrib[CONST_RESISTANCE_ATR])])

    for capactor in capactors:
        from_net = int(capactor.attrib[CONST_NET_FROM_ATR])
        to_net = int(capactor.attrib[CONST_NET_TO_ATR])
        edges_list.append([from_net, to_net, float(capactor.attrib[CONST_RESISTANCE_ATR])])
        edges_list.append([to_net, from_net, float(capactor.attrib[CONST_RESISTANCE_ATR])])

    for diod in diodes:
        from_net = int(diod.attrib[CONST_NET_FROM_ATR])
        to_net = int(diod.attrib[CONST_NET_TO_ATR])
        edges_list.append([from_net, to_net, float(diod.attrib[CONST_RESISTANCE_ATR])])
        edges_list.append([to_net, from_net, float(diod.attrib[CONST_REVERSE_RESISTANCE_ATR])])
    return edges_list


def form_matrix_of_resistance(nodes, edges):
    num_of_nodes = len(nodes)
    matrix = []
    for i in range(num_of_nodes):
        matrix.append([float("+inf")] * num_of_nodes)
        matrix[i][i] = 0

    for edge in edges:
        i = nodes.index(edge[0])
        j = nodes.index(edge[1])
        weight = edge[2]
        if matrix[i][j] == 0:
            matrix[i][j] = 0
        else:
            matrix[i][j] = 1 / (1 / matrix[i][j] + 1 / weight)

    for k in range(num_of_nodes):
        for i in range(num_of_nodes):
            for j in range(num_of_nodes):
                if matrix[i][j] == 0 or matrix[i][k] + matrix[k][j] == 0:
                    matrix[i][j] = 0
                elif 1 / matrix[i][j] + 1 / (matrix[i][k] + matrix[k][j]) == 0:
                    matrix[i][j] = float("+inf")
                else:
                    matrix[i][j] = 1 / (1 / matrix[i][j] + 1 / (matrix[i][k] + matrix[k][j]))

    return matrix


def write_matrix_into_csv(file_address, matrix):
    num_of_elems = len(matrix)
    with open(file_address, "w") as file:
        for i in range(num_of_elems):
            for j in range(num_of_elems):
                if j == num_of_elems - 1:
                    file.write(str(round(matrix[i][j], 6)))
                else:
                    file.write(str(round(matrix[i][j], 6)) + ",")
            file.write("\n")


def floyd_warshall_from_xml_to_csv(xml_address, csv_address):
    tree = ElementTree.parse(xml_address)
    matr = form_matrix_of_resistance(form_nodes_list(tree), form_edges_list(tree))
    write_matrix_into_csv(csv_address, matr)

def c_floyd_warshall_from_xml_to_csv(xml_address, csv_address):
    tree = ElementTree.parse(xml_address)
    matr = fwalg.form_resistance_matrix(form_nodes_list(tree), form_edges_list(tree))
    write_matrix_into_csv(csv_address, matr)


def main(argv):
    py_start_time = time.time()
    floyd_warshall_from_xml_to_csv(argv[0], argv[1])
    py_end_time = time.time()

    c_start_time = time.time()
    c_floyd_warshall_from_xml_to_csv(argv[0], argv[1])
    c_end_time = time.time()
    frac = (py_end_time - py_start_time)/(c_end_time - c_start_time)
    print('python time divided by c++ time equals {0:.4f}'.format(frac))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1:])
    else:
        print("Error of using the program\n", "usage: hw1.py <input_xml_file> <output_csv_file>")
