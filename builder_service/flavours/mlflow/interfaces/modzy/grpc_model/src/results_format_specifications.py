"""
{
    "classPredictions": [
        {"class": <class-1-label>, "score": <class-1-probability>},
        ...,
        {"class": <class-n-label>, "score": <class-n-probability>}
    ]
}
"""

classification_schema = {
    "type": "object",
    "properties": {
        "classPredictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"class": {"type": "string"}, "score": {"type": "number"}},
                "required": ["class", "score"],
            },
        }
    },
    "additionalProperties": False,
}

"""
{
    "detections": [
        {
            "xMin": <detection-1-xmin>,
            "xMax": <detection-1-xmax>,
            "yMin": <detection-1-ymin>,
            "yMax": <detection-1-ymax>,
            "class": <detection-1-class>,
            "objectProbability": <optional-detection-1-object-probability>,
            "classProbability": <optional-detection-1-class-probability>,
        }
        ...,
        {
            "xMin": <detection-n-xmin>,
            "xMax": <detection-n-xmax>,
            "yMin": <detection-n-ymin>,
            "yMax": <detection-n-ymax>,
            "class": <detection-n-class>,
            "objectProbability": <optional-detection-n-object-probability>,
            "classProbability": <optional-detection-n-class-probability>,
        }
    ]
}
"""

object_detection_schema = {
    "type": "object",
    "properties": {
        "detections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "xMin": {"type": "number"},
                    "xMax": {"type": "number"},
                    "yMin": {"type": "number"},
                    "yMax": {"type": "number"},
                    "class": {"type": "string"},
                    "objectProbability": {"type": "number"},
                    "classProbability": {"type": "number"},
                },
                "required": ["xMin", "xMax", "yMin", "yMax", "class"],
            },
        }
    },
    "additionalProperties": False,
}

"""
{
    "instances": [
        {
            "maskRLE": <instance-1-rle-mask>,
            "class": <instance-1-class>,
            "objectProbability": <optional-instance-1-object-probability>,
            "xMin": <optional-instance-1-xmin>,
            "xMax": <optional-instance-1-xmax>,
            "yMin": <optional-instance-1-ymin>,
            "yMax": <optional-instance-1-ymax>,        
        }
        ...,
        {
            "maskRLE": <instance-n-rle-mask>,
            "class": <instance-n-class>,
            "objectProbability": <optional-instance-n-object-probability>,
            "xMin": <optional-instance-n-xmin>,
            "xMax": <optional-instance-n-xmax>,
            "yMin": <optional-instance-n-ymin>,
            "yMax": <optional-instance-n-ymax>,        
        }
    ]
}
"""

instance_segmentation_schema = {
    "type": "object",
    "properties": {
        "instances": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "class": {"type": "string"},
                    "maskRLE": {"type": "array", "items": {"type": "number"}},
                    "objectProbability": {"type": "number"},
                    "xMin": {"type": "number"},
                    "xMax": {"type": "number"},
                    "yMin": {"type": "number"},
                    "yMax": {"type": "number"},
                },
                "required": [
                    "class",
                    "maskRLE",
                ],
            },
        },
        "imageDimensions": {
            "type": "object",
            "properties": {"height": {"type": "number"}, "width": {"type": "number"}},
            "required": ["height", "width"],
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

"""
{
  "segmentation": {
    "maskRLE": {
      "frequencies": <frequency-array>,
      "encoding": <string-encoding-classes>
    }
  },
  "encodingMap":  {
    <class-name-value-pairs>
  },
  "imageDimensions": {
      "height": 8,
      "width": 8
  }
}
"""

semantic_segmentation_schema = {
    "type": "object",
    "properties": {
        "segmentation": {
            "type": "object",
            "properties": {
                "maskRLE": {
                    "type": "object",
                    "properties": {
                        "frequencies": {"type": "array", "items": {"type": "number"}},
                        "encoding": {"type": "string"},
                    },
                    "required": ["frequencies", "encoding"],
                },
            },
            "required": ["maskRLE"],
        },
        "encodingMap": {
            "type": "object",
        },
        "imageDimensions": {
            "type": "object",
            "properties": {"height": {"type": "number"}, "width": {"type": "number"}},
            "required": ["height", "width"],
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

"""
{
    "text": <generated-text-content>,
    "type": <optional-type-of-text-generated>,
    "description": <optional-description-of-text>,
    "value": <optional-numerical-value-of-text>
}
"""

text_generation_schema = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "type": {"type": "string"},
        "description": {"type": "string"},
        "value": {"type": "number"},
    },
    "required": ["text"],
}
