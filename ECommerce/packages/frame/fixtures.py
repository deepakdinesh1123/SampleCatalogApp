#TODO: Modify fixture to work without pk's
[
{
  "model": "permissions.policymodel",
  "pk": 2,
  "fields": {
    "created_at": "2023-09-08T09:44:58.687Z",
    "created_by": "",
    "modified_at": "2023-09-08T10:58:02.845Z",
    "modified_by": "",
    "name": "FrameConfigurationView",
    "description": "",
    "statement": {
      "permissions": [
        {
          "name": "packages.frame.configure.views.FrameConfigureView",
          "type": "view"
        }
      ]
    },
    "expiry": null,
    "is_active": true
  }
},
{
  "model": "permissions.policymodel",
  "pk": 3,
  "fields": {
    "created_at": "2023-09-08T10:29:12.655Z",
    "created_by": "",
    "modified_at": "2023-09-09T07:13:24.235Z",
    "modified_by": "",
    "name": "FramesModel",
    "description": "",
    "statement": {
      "permissions": [
        {
          "name": "FramesModel",
          "type": "model",
          "actions": [
            "view",
            "create",
            "edit",
            "delete"
          ],
          "records": {
            "field": "id",
            "value": 1,
            "operation": "gte"
          }
        }
      ]
    },
    "expiry": null,
    "is_active": true
  }
},
{
  "model": "permissions.policymodel",
  "pk": 4,
  "fields": {
    "created_at": "2023-09-09T07:59:47.163Z",
    "created_by": "",
    "modified_at": "2023-09-09T07:59:47.163Z",
    "modified_by": "",
    "name": "FrameTestView",
    "description": "",
    "statement": {
      "permissions": [
        {
          "name": "module1.views.FrameTestView",
          "type": "view"
        }
      ]
    },
    "expiry": null,
    "is_active": true
  }
}
]
