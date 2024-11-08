
class Scanner:

    _VALUE_DELIM = "="

    @classmethod
    def scan(cls, filename, *requested):
        scanned = {}

        with open(filename, "r") as f:
            for line in f.readlines():
                if line.strip():
                    key, value = (x.strip() for x in line.split(cls._VALUE_DELIM))
                    scanned[key] = cls.infer_type(value)
        
        if not requested:
            return scanned
        return {k:v for k, v in scanned.items() if k in requested}

    @staticmethod
    def infer_type(value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value


class _Configurable:

    _CONFIG_ATTRS = {
        # Attribute: (key in conf, default)
    }

    def __new__(cls, *args, **kwargs):
        for attr, (key, default) in cls._CONFIG_ATTRS.items():
            value = kwargs.get(key, default)
            setattr(cls, attr, value)
        return super().__new__(cls)
