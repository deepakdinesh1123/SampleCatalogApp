import copy

field_map = {
    "BigAutoField": {
        "type": "integer",
        "searchable": True,
        "sortable": True,
    },
    "AutoField": {
        "type": "integer",
        "searchable": True,
        "sortable": True,
    },
    "CharField": {
        "type": "string",
        "searchable": True,
        "sortable": True,
    },
    "IntegerField": {
        "type": "integer",
        "searchable": True,
        "sortable": True,
    },
    "PositiveIntegerField": {
        "type": "integer",
        "searchable": True,
        "sortable": True,
    },
    "FloatField": {
        "type": "float",
        "searchable": True,
        "sortable": True,
    },
    "BooleanField": {
        "type": "boolean",
        "searchable": True,
        "sortable": True,
    },
    "DateField": {
        "type": "date",
        "searchable": True,
        "sortable": True,
    },
    "DateTimeField": {
        "type": "datetime",
        "searchable": True,
        "sortable": True,
    },
    "EmailField": {
        "type": "email",
        "searchable": True,
        "sortable": True,
    },
    "PhoneNumberField": {
        "type": "string",
        "searchable": True,
        "sortable": True,
    },
    "ZFileField": {
        "type": "file",
        "searchable": False,
        "sortable": False,
    },
    "ImageField": {
        "type": "image",
        "searchable": False,
        "sortable": False,
    },
    "DecimalField": {
        "type": "decimal",
        "searchable": True,
        "sortable": True,
    },
    "TextField": {
        "type": "string",
        "searchable": True,
        "sortable": False,
    },
    "UUIDField": {
        "type": "uuid",
        "searchable": True,
        "sortable": True,
    },
    "ZOneToOneField": {"type": "string", "searchable": True, "sortable": True},
    "ZForeignKey": {"type": "string", "searchable": True, "sortable": True},
    "ForeignKey": {"type": "string", "searchable": True, "sortable": True},
    "JSONField": {"type": "json", "searchable": False, "sortable": False},
    "ArrayField": {"type": "array", "searchable": False, "sortable": False},
    "URLField": {"type": "url", "searchable": True, "sortable": True},
}


class ModelCol:
    model_field = None
    display_as = None
    _type = None
    searchable = None
    sortable = None
    choices = None

    def __init__(self, *args, **kwargs):
        self.display_as = kwargs.get("display_as", None)
        self._type = kwargs.get("type", None)
        self.searchable = kwargs.get("searchable", None)
        self.sortable = kwargs.get("sortable", None)
        self.choices = kwargs.get("choices", None)
        self.user_roles = kwargs.get("user_roles", [])
        self.related_object_attribute = kwargs.get("related_object_attribute", None)

    def update_model_field(self, field):
        self.model_field = field

    def get_col_metadata(self, request, col_index):
        metadata = copy.deepcopy(field_map[self.model_field.__class__.__name__])
        metadata.update(name=self.model_field.name)
        if self.display_as:
            metadata.update(display_name=self.display_as)
        if self._type:
            metadata.update(type=self._type)
        if self.searchable is not None:
            metadata.update(searchable=self.searchable)
        if self.sortable is not None:
            metadata.update(sortable=self.sortable)
        if self.model_field.choices:
            choices_list = [
                {"id": c[0], "label": c[1]} for c in self.model_field.choices
            ]
            metadata.update(choices=choices_list)
        if self.related_object_attribute is not None:
            metadata.update(related_object_attribute=self.related_object_attribute)
        if request:
            search_query = request.GET.get(f"columns[{col_index}][search][value]")
            metadata.update(search_query=search_query)

        return metadata


class StringCol:
    def __init__(self, *args, **kwargs):
        self.searchable = kwargs.get("searchable", False)
        self.sortable = kwargs.get("sortable", False)
        self.user_roles = kwargs.get("user_roles", [])
        self.display_as = kwargs.get("display_as", None)
        self.choices = kwargs.get("choices", [])

    def update_model_name(self, name):
        self.name = name
        return

    def update_properties(self, request, properties):
        if properties.get("choices"):
            choices_method = properties["choices"].get("choices_method")
            if choices_method:
                choices = choices_method(request)
                self.choices = choices

    def get_col_metadata(self, request, col_index):
        metadata = {
            "type": "string",
            "name": self.name,
            "searchable": self.searchable,
            "sortable": self.sortable,
        }
        if self.display_as:
            metadata.update(display_name=self.display_as)
        if self.choices:
            choices_list = [{"id": c[0], "label": c[1]} for c in self.choices]
            metadata.update(choices=choices_list)

        if request:
            search_query = request.GET.get(f"columns[{col_index}][search][value]")
            metadata.update(search_query=search_query)
        return metadata


class NumericCol:
    def __init__(self, *args, **kwargs):
        pass


class SelectCol:
    def __init__(self, *args, **kwargs):
        pass
