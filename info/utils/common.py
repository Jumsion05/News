def do_index_class(index):
    """自定义过滤器,过滤点击排序html的class"""
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""