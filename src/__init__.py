# src/__init__.py
from .data_schema import (
    BuildingObject, ObjectCategory, ObjectLibrary,
    Geometry, Semantic, PhysicsProperties, BoundingBox,
    create_furniture_templates, create_appliance_templates,
)
from .scene_graph_builder import (
    SceneGraph, SceneEdge, SpatialRelation,
    VRSceneBuilder, CADSceneBuilder, SceneGraphDatabase,
)
from .neural import (
    VisionEncoder, ImageEncoder,
    PhysicsMLP, PropertyPredictor,
    RelationTransformer, SceneEncoder,
    Trainer, build_training_data,
)

__all__ = [
    # Data schema
    "BuildingObject",
    "ObjectCategory",
    "ObjectLibrary",
    "Geometry",
    "Semantic",
    "PhysicsProperties",
    "BoundingBox",
    "create_furniture_templates",
    "create_appliance_templates",
    # Scene graph
    "SceneGraph",
    "SceneEdge",
    "SpatialRelation",
    "VRSceneBuilder",
    "CADSceneBuilder",
    "SceneGraphDatabase",
    # Neural
    "VisionEncoder",
    "ImageEncoder",
    "PhysicsMLP",
    "PropertyPredictor",
    "RelationTransformer",
    "SceneEncoder",
    "Trainer",
    "build_training_data",
]
