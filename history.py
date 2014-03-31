
class History(object):
    """
    History of requests
    """
    def __init__(self, path):
        self.path = path

    def _last(self):
        try:
            with open(os.path.join(self.path, 'HEAD')) as f:
                return int(f.read().strip())
        except IOError:
            return 0

    def _fname(self, index):
        return '{:0=5d}'.format(index)

    def _fpath(self, index):
        return os.path.join(self.path, self._fname(index))

    def _extract_item(self, fpath, index=None, include_body=True):
        with open(fpath) as f:
            lines = f.readlines()
            body = reduce(add, lines[2:], '') or None if include_body else None
            return HistoryItem(lines[0].strip(), lines[1].strip(), body=body, index=index)

    def items(self, include_body=True):
        try:
            last = self._last()
            for findex in xrange(last, 0, -1):
                yield self._extract_item(self._fpath(findex), index=(last - findex + 1),
                                         include_body=include_body)
        except IOError:
            # Stop processing on any error
            pass

    def __getitem__(self, index):
        return self._extract_item(self._fpath(self._last() + 1 - index),
                                  include_body=True)

    def store_item(self, method, resource, body):
        # TODO: Should it take `HistoryItem` as arg?
        last = self._last()
        # Do not store if it is same as last item
        try:
            last_item = self._extract_item(self._fpath(last))
            if last_item == HistoryItem(method, resource, body=body):
                return
        except IOError:
            # last item does not exist
            pass
        new_filepath = self._fpath(last + 1)
        with open(new_filepath, 'w') as f:
            args = body and (method, resource, body) or (method, resource, )
            print(*args, sep='\n', file=f)
            with open(os.path.join(self.path, 'HEAD'), 'w') as hf:
                hf.write(self._fname(last + 1))


class HistoryItem(object):
    # TODO: Since an item is a request not something generic, should the name
    # be changed to Request?

    def __init__(self, method, resource, body=None, index=None):
        self.method = method
        self.resource = resource
        self.body = body
        self.index = index

    def printable(self):
        return '{:<6}{:<10}{}'.format(self.index, self.method, self.resource)

    def __eq__(self, other):
        return isinstance(other, HistoryItem) and self.__dict__ == other.__dict__


