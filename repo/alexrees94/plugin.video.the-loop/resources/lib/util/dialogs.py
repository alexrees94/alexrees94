import xbmcgui
hide_link = True

def link_dialog(links, return_idx=False):
    if len(links) == 1:
        link = links[0]
        if "(" in link and link.endswith(")"):
            split = link.split('(')
            link = split[0]
        return link if not return_idx else 0
    options = []
    for i, link in enumerate(links):
        if "(" in link and link.endswith(")"):
            split = link.split('(')
            label = split[-1].replace(')', '')
            options.append(label) if hide_link else options.append("%s - %s" % (label, split[0]))
            links[i] = split[0]
        else:
            options.append("Link " + str(i + 1)) if hide_link else options.append(link)
    idx = xbmcgui.Dialog().select("Choose a link", options)
    if idx == -1: return None
    return links[idx] if not return_idx else idx
