import { Group, NotificationType, RawAttribute, RawCatalogueEntry, RawCommunicationLog, RawCustodian,
  RawEmailNotification, RawLayerSubmission, RawLayerSubscription, RawMetadata, RawSymbology, RawUser, RawWebhookNotification, RecordStatus
} from "./backend.api";
import { CommunicationLogType, LogEnum } from "../providers/logsProvider.api";

export let DUMMY_CATALOGUE_ENTRIES: Array<RawCatalogueEntry> = [
  {
    "id": 1,
    "name": "Catalogue Entry 1",
    "description": "This is the first example catalogue entry",
    "status": 1,
    "created_at": "2022-10-11T12:44:15.562984Z",
    "updated_at": "2022-10-13T04:26:24.629841Z",
    "custodian": 1,
    "assigned_to": 1,
    "subscription": 1,
    "active_layer": 1,
    "layers": [1],
    "email_notifications": [1],
    "webhook_notifications": [1],
    "editors": [1, 2],
    "workspace": 1,
    "metadata": 1
  },
  {
    "id": 2,
    "name": "Catalogue Entry 2",
    "description": "This is the second example catalogue entry",
    "status": 2,
    "created_at": "2022-10-11T12:44:15.562984Z",
    "updated_at": "2022-10-12T21:05:32.325153Z",
    "custodian": 2,
    "assigned_to": 3,
    "subscription": 2,
    "active_layer": 2,
    "layers": [2],
    "email_notifications": [2],
    "webhook_notifications": [2],
    "editors": [2, 3],
    "workspace": 2,
    "metadata": 2
  },
  {
    "id": 3,
    "name": "Catalogue Entry 3",
    "description": "This is the third example catalogue entry",
    "status": 3,
    "created_at": "2022-10-11T12:44:15.562984Z",
    "updated_at": "2022-10-11T12:44:15.562984Z",
    "custodian": 2,
    "assigned_to": undefined,
    "subscription": 3,
    "active_layer": 3,
    "layers": [3],
    "email_notifications": [3],
    "webhook_notifications": [3],
    "editors": [3],
    "workspace": 3,
    "metadata": 3
  }
];

export const DUMMY_LAYER_SUBSCRIPTIONS: Array<RawLayerSubscription> = [
  {
    "id": 1,
    "name": "Layer Subscription 1",
    "url": "https://www.abc.net.au/",
    "frequency": "1 11:11:11",
    "status": 1,
    "subscribed_at": "2022-10-13T02:11:02.818232Z",
    "catalogue_entry": 1
  }, {
    "id": 2,
    "name": "Layer Subscription 2",
    "url": "https://www.sbs.com.au/",
    "frequency": "2 22:22:22",
    "status": 2,
    "subscribed_at": "2022-10-12T23:53:32.756754Z",
    "catalogue_entry": 2
  }, {
    "id": 3,
    "name": "Layer Subscription 3",
    "url": "https://www.nit.com.au/",
    "frequency": "4 09:33:33",
    "status": 3,
    "subscribed_at": "2022-10-11T13:27:12.345346Z",
    "catalogue_entry": 3
  }
];

export const DUMMY_LAYER_SUBMISSIONS: Array<RawLayerSubmission> = [
  {
    "id": 1,
    "name": "Layer Submission 1",
    "description": "This is the first example layer submission",
    "file": "https://www.google.com/",
    "status": 1,
    "submitted_at": "2022-10-13T04:11:05.195734Z",
    "catalogue_entry": 1,
    "attributes": [
      1,
      2,
      3
    ],
    "metadata": 1,
    "symbology": 1
  },
  {
    "id": 2,
    "name": "Layer Submission 2",
    "description": "This is the second example layer submission",
    "file": "https://www.yahoo.com/",
    "status": 2,
    "submitted_at": "2022-10-12T07:56:15.665294Z",
    "catalogue_entry": 2,
    "attributes": [
      4,
      5,
      6
    ],
    "metadata": 2,
    "symbology": 2
  },
  {
    "id": 3,
    "name": "Layer Submission 3",
    "description": "This is the third example layer submission",
    "file": "https://www.bing.com/",
    "status": 3,
    "submitted_at": "2022-10-11T11:24:42.816585Z",
    "catalogue_entry": 3,
    "attributes": [
      7,
      8,
      9
    ],
    "metadata": 3,
    "symbology": 3
  }
];

export const DUMMY_STATUSES: Array<RecordStatus<unknown>> = [
  { "id": 1, "label": "Draft" },
  { "id": 2, "label": "Locked" },
  { "id": 3, "label": "Cancelled" }
];

export const DUMMY_USERS: Array<RawUser> = [
  { "id": 1, "username": "Raoul Wallenberg", "groups": [0] },
  { "id": 2, "username": "Carl Lutz", "groups": [0] },
  { "id": 3, "username": "Chiune Sugihara", "groups": [0] }
];

export const DUMMY_EMAIL_NOTIFICATIONS: Array<RawEmailNotification> = [
  {
    "id": 1,
    "name": "Email Notification 1",
    "type": 1,
    "email": "cat@example.com",
    "catalogue_entry": 1
  },
  {
    "id": 2,
    "name": "Email Notification 2",
    "type": 2,
    "email": "dog@example.com",
    "catalogue_entry": 2
  },
  {
    "id": 3,
    "name": "Email Notification 3",
    "type": 3,
    "email": "bird@example.com",
    "catalogue_entry": 3
  }
];

export const DUMMY_WEBHOOK_NOTIFICATIONS: Array<RawWebhookNotification> = [
  {
    "id": 1,
    "name": "Webhook Notification 1",
    "type": 1,
    "url": "https://www.dbca.wa.gov.au/",
    "catalogue_entry": 1
  },
  {
    "id": 2,
    "name": "Webhook Notification 2",
    "type": 2,
    "url": "https://www.dpaw.wa.gov.au/",
    "catalogue_entry": 2
  },
  {
    "id": 3,
    "name": "Webhook Notification 3",
    "type": 3,
    "url": "https://www.dcceew.gov.au/",
    "catalogue_entry": 3
  }
];

export const DUMMY_EMAIL_NOTIFICATION_TYPES: Array<NotificationType> = [
  {
    "id": 1,
    "label": "On Approve"
  },
  {
    "id": 2,
    "label": "On Lock"
  },
  {
    "id": 3,
    "label": "Both"
  }
];

export const DUMMY_WEBHOOK_NOTIFICATION_TYPES: Array<NotificationType> = [
  {
    "id": 1,
    "label": "On Approve"
  },
  {
    "id": 2,
    "label": "On Lock"
  },
  {
    "id": 3,
    "label": "Both"
  }
];

export const DUMMY_SYMBOLOGIES: Array<RawSymbology> = [
  {
    "id": 0,
    "name": "string",
    "sld": "string",
    "catalogue_entry": 0
  }
];

export const DUMMY_ATTRIBUTES: Array<RawAttribute> = [
  {
    "id": 3,
    "name": "LGA_DATE_TIME",
    "type": "DateTime",
    "order": 3,
    "catalogue_entry": 1
  },
  {
    "id": 4,
    "name": "LGA_NAME1",
    "type": "String",
    "order": 4,
    "catalogue_entry": 1
  },
  {
    "id": 5,
    "name": "LGA_LGA_NAME",
    "type": "String",
    "order": 5,
    "catalogue_entry": 1
  },
  {
    "id": 6,
    "name": "LGA_TYPE",
    "type": "String",
    "order": 6,
    "catalogue_entry": 1
  },
  {
    "id": 7,
    "name": "LGA_LABEL",
    "type": "String",
    "order": 7,
    "catalogue_entry": 1
  },
  {
    "id": 8,
    "name": "LGA_LEGAL_AREA",
    "type": "Real",
    "order": 8,
    "catalogue_entry": 1
  },
  {
    "id": 9,
    "name": "SHAPE_Length",
    "type": "Real",
    "order": 9,
    "catalogue_entry": 1
  },
  {
    "id": 10,
    "name": "SHAPE_Area",
    "type": "Real",
    "order": 10,
    "catalogue_entry": 1
  },
  {
    "id": 11,
    "name": "OBJECTID",
    "type": "Integer64",
    "order": 1,
    "catalogue_entry": 2
  },
  {
    "id": 12,
    "name": "LOC_LOCALITY_NAME",
    "type": "String",
    "order": 2,
    "catalogue_entry": 2
  },
  {
    "id": 13,
    "name": "LOC_POSTCODE",
    "type": "String",
    "order": 3,
    "catalogue_entry": 2
  },
  {
    "id": 14,
    "name": "LOC_CREATE_DATE",
    "type": "DateTime",
    "order": 4,
    "catalogue_entry": 2
  },
  {
    "id": 15,
    "name": "LOC_LEGAL_AREA",
    "type": "Real",
    "order": 5,
    "catalogue_entry": 2
  },
  {
    "id": 16,
    "name": "SHAPE_Length",
    "type": "Real",
    "order": 6,
    "catalogue_entry": 2
  },
  {
    "id": 17,
    "name": "SHAPE_Area",
    "type": "Real",
    "order": 7,
    "catalogue_entry": 2
  }
];

export const DUMMY_METADATA_LIST: Array<RawMetadata> = [
  {
    "id": 0,
    "name": "string",
    "created_at": "2022-11-25T06:57:28.139Z",
    "catalogue_entry": 0
  }
];

export const DUMMY_CUSTODIANS: Array<RawCustodian> = [
  {
    "id": 0,
    "name": "string",
    "contact_name": "string",
    "contact_email": "user@example.com",
    "contact_phone": "string"
  }
];

export const DUMMY_GROUPS: Array<Group> = [
  {
    "id": 0,
    "name": "string"
  }
];

export const DUMMY_COMM_LOGS: Array<RawCommunicationLog> = [
  {
    "id": 1,
    "created_at": "2022-12-21T14:50:30.884033Z",
    "type": 3,
    "to": "Punny Hot",
    "cc": "Belly Jeans",
    "from": "Bunny Phone",
    "subject": "The thing about the stuff",
    "text": "Y'know... the thing? With the stuff?",
    "documents": [],
    "user": 1
  },
  {
    "id": 2,
    "created_at": "2022-12-21T14:50:31.693187Z",
    "type": 3,
    "to": "Bunny Phone",
    "cc": "Punny Hot",
    "from": "Belly Jeans",
    "subject": "The other thing I mentioned",
    "text": "He just trailed off after that",
    "documents": [],
    "user": 1
  },
  {
    "id": 3,
    "created_at": "2022-12-21T14:50:32.064073Z",
    "type": 3,
    "to": "Belly Jeans",
    "cc": "Bunny Phone",
    "from": "Punny Hot",
    "subject": "Wisdom of the ages",
    "text": "You can lead an early bird to water, but you can't make it do the worm.",
    "documents": [],
    "user": 1
  }
];

export const DUMMY_COMM_LOG_TYPES: Array<CommunicationLogType> = [
  {
    "id": 1,
    "label": LogEnum.Email
  },
  {
    "id": 2,
    "label": LogEnum.Phone
  },
  {
    "id": 3,
    "label": LogEnum.Mail
  },
  {
    "id": 4,
    "label": LogEnum.Person
  },
  {
    "id": 5,
    "label": LogEnum.Other
  }
];
