import os
import json


def load_map_data():
    map_file_name = "map_new.json"
    with open(map_file_name, encoding="utf8") as map_file:
        raw_map_dict = json.load(map_file)

    map_info_dict = {"node": {}, "way": {}}
    for element in raw_map_dict["elements"]:
        element_type = element["type"]

        if element_type == "node":
            node_id = element["id"]
            latitude = element["lat"]
            longitude = element["lon"]

            tags = None
            if "tags" in element.keys():
                tags = element["tags"]

            local_node = {"node_id": node_id, "latitude": latitude,
                          "longitude": longitude, "tags": tags}
            map_info_dict["node"][node_id] = local_node
        elif element_type == "way":
            way_id = element["id"]
            nodes_list = element["nodes"]

            tags = None
            if "tags" in element.keys():
                tags = element["tags"]

            local_way = {"way_id": way_id, "nodes_list": nodes_list, "tags": tags}
            map_info_dict["way"][way_id] = local_way
    return map_info_dict


def load_node_data():
    node_info_file_name = "node_info.json"
    with open(node_info_file_name, "r") as node_info_file:
        node_info_dict = json.load(node_info_file)
    return node_info_dict


def get_phase_link(map_dict, way_list, node_id):
    # first step is to sequence the node id of the way list
    sequenced_node_list = []
    for way_idx in range(len(way_list) - 1):
        up_way_list = map_dict["way"][way_list[way_idx]]["nodes_list"]
        down_way_list = map_dict["way"][way_list[way_idx + 1]]["nodes_list"]

        if len(sequenced_node_list) == 0:
            if up_way_list[0] == down_way_list[0]:
                sequenced_node_list += up_way_list[::-1]
                sequenced_node_list += down_way_list[1:]
            elif up_way_list[0] == down_way_list[-1]:
                sequenced_node_list += up_way_list[::-1]
                sequenced_node_list += down_way_list[::-1][1:]
            elif up_way_list[-1] == down_way_list[0]:
                sequenced_node_list += up_way_list
                sequenced_node_list += down_way_list[1:]
            elif up_way_list[-1] == down_way_list[-1]:
                sequenced_node_list += up_way_list
                sequenced_node_list += down_way_list[::-1][1:]
            else:
                return None
            continue

        if down_way_list[0] == sequenced_node_list[-1]:
            sequenced_node_list += down_way_list[1:]
        elif down_way_list[-1] == sequenced_node_list[-1]:
            sequenced_node_list += down_way_list[::-1][1:]
        else:
            return None

    in_link_node_list = []
    out_link_node_list = []
    current_flag = False
    for current_node in sequenced_node_list:
        if current_node == node_id:
            current_flag = True
            in_link_node_list.append(current_node)
            out_link_node_list.append(current_node)

        if current_flag:
            out_link_node_list.append(current_node)
        else:
            in_link_node_list.append(current_node)

    return [in_link_node_list, out_link_node_list]


def generate_map():
    map_info_dict = load_map_data()
    node_info_dict = load_node_data()

    node_location_dict = {}
    link_location_dict = {}
    node_phase_link_dict = {}

    for element in node_info_dict["signal_node"]:
        node_id = element["node_id"]
        phases = element["phases"]

        node_location_dict[node_id] = {"latitude": map_info_dict["node"][node_id]["latitude"],
                                       "longitude": map_info_dict["node"][node_id]["longitude"]}
        if not (node_id in node_phase_link_dict):
            node_phase_link_dict[node_id] = {}

        for phase in phases:
            phase_id = phase["phase_id"]
            way_list = phase["ways"]
            link_info = get_phase_link(map_info_dict, way_list, node_id)

            if link_info is None:
                print("Node", node_id, "phase", phase_id, "input info incorrect!")
                continue

            in_link_id = str(node_id) + str(phase_id) + "0"
            out_link_id = str(node_id) + str(phase_id) + "1"

            node_phase_link_dict[node_id][phase_id] = {"in_link_id": in_link_id, "out_link_id": out_link_id}

            link_location_dict[in_link_id] = {"latitudes": [], "longitudes": []}
            for temp_node_id in link_info[0]:
                current_node = map_info_dict["node"][temp_node_id]
                link_location_dict[in_link_id]["latitudes"].append(current_node["latitude"])
                link_location_dict[in_link_id]["longitudes"].append(current_node["longitude"])

            link_location_dict[out_link_id] = {"latitudes": [], "longitudes": []}
            for temp_node_id in link_info[1]:
                current_node = map_info_dict["node"][temp_node_id]
                link_location_dict[out_link_id]["latitudes"].append(current_node["latitude"])
                link_location_dict[out_link_id]["longitudes"].append(current_node["longitude"])

    # output all the information
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    node_location_file_name = "nodes.csv"
    with open(os.path.join(output_folder, node_location_file_name), "w") as node_location_file:
        node_location_file.write("node_id, Latitude, Longitude, Comment\n")
        for node_id in node_location_dict:
            node_latitude = node_location_dict[node_id]["latitude"]
            node_longitude = node_location_dict[node_id]["longitude"]
            lines_info = ",".join([str(val) for val in [node_id, node_latitude, node_longitude]]) + ",\n"
            node_location_file.write(lines_info)

    link_location_file_name = "link_points.csv"
    with open(os.path.join(output_folder, link_location_file_name), "w") as link_location_file:
        link_location_file.write("Node id, Latitude, Longitude\n")
        for link_id in link_location_dict.keys():
            link_info = link_location_dict[link_id]
            link_latitudes = link_info["latitudes"]
            link_longitudes = link_info["longitudes"]

            for idx in range(len(link_latitudes)):
                local_lat = link_latitudes[idx]
                local_lon = link_longitudes[idx]

                lines_info = ",".join([str(val) for val in [link_id, local_lat, local_lon]]) + "\n"
                link_location_file.write(lines_info)

    phase_info_file_name = "movements.csv"
    with open(os.path.join(output_folder, phase_info_file_name), "w") as phase_info_file:
        phase_info_file.write("node id, phase id, in link, out link\n")
        for node_id in node_phase_link_dict.keys():
            node_info = node_phase_link_dict[node_id]

            for phase_id in node_info.keys():
                in_link_id = node_info[phase_id]["in_link_id"]
                out_link_id = node_info[phase_id]["out_link_id"]
                lines_info = ",".join([str(val) for val in
                                       [node_id, phase_id, in_link_id, out_link_id]]) + "\n"
                phase_info_file.write(lines_info)


if __name__ == '__main__':
    generate_map()

