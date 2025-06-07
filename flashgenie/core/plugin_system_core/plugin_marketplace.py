"""
FlashGenie Plugin Marketplace

Provides plugin discovery, rating, review, and distribution capabilities
for the FlashGenie plugin ecosystem.
"""

import json
import hashlib
try:
    import requests
except ImportError:
    requests = None
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from .plugin_system import PluginManifest, PluginType
from flashgenie.utils.exceptions import FlashGenieError


class MarketplaceCategory(Enum):
    """Plugin marketplace categories."""
    OFFICIAL = "official"
    FEATURED = "featured"
    POPULAR = "popular"
    NEW = "new"
    EDUCATIONAL = "educational"
    ACCESSIBILITY = "accessibility"
    PRODUCTIVITY = "productivity"
    EXPERIMENTAL = "experimental"


@dataclass
class PluginRating:
    """Plugin rating and review data."""
    user_id: str
    rating: float  # 1.0 to 5.0
    review: str
    date: datetime
    helpful_votes: int = 0
    verified_purchase: bool = False


@dataclass
class PluginStats:
    """Plugin marketplace statistics."""
    downloads: int = 0
    active_users: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    compatibility_score: float = 1.0
    security_score: float = 1.0


@dataclass
class MarketplacePlugin:
    """Plugin information in marketplace."""
    manifest: PluginManifest
    stats: PluginStats
    ratings: List[PluginRating] = field(default_factory=list)
    categories: List[MarketplaceCategory] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    changelog: str = ""
    price: float = 0.0  # 0.0 for free plugins
    license_type: str = "MIT"
    support_url: Optional[str] = None
    documentation_url: Optional[str] = None
    verified: bool = False
    featured: bool = False


class PluginMarketplace:
    """Plugin marketplace for discovery and distribution."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the plugin marketplace."""
        self.cache_dir = cache_dir or Path("data/marketplace_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("plugin_marketplace")
        
        # Marketplace configuration
        self.marketplace_url = "https://plugins.flashgenie.org"  # Hypothetical URL
        self.api_version = "v1"
        self.cache_duration = timedelta(hours=6)
        
        # Local plugin registry
        self.local_plugins: Dict[str, MarketplacePlugin] = {}
        self.featured_plugins: List[str] = []
        
        # Load cached data
        self._load_cache()
    
    def search_plugins(self, query: str = "", 
                      plugin_type: Optional[PluginType] = None,
                      category: Optional[MarketplaceCategory] = None,
                      min_rating: float = 0.0,
                      free_only: bool = False,
                      limit: int = 20) -> List[MarketplacePlugin]:
        """Search for plugins in the marketplace."""
        self.logger.info(f"Searching plugins: query='{query}', type={plugin_type}, category={category}")
        
        # Refresh cache if needed
        self._refresh_cache_if_needed()
        
        results = []
        
        for plugin in self.local_plugins.values():
            # Apply filters
            if plugin_type and plugin.manifest.plugin_type != plugin_type:
                continue
            
            if category and category not in plugin.categories:
                continue
            
            if plugin.stats.average_rating < min_rating:
                continue
            
            if free_only and plugin.price > 0.0:
                continue
            
            # Apply text search
            if query:
                search_text = f"{plugin.manifest.name} {plugin.manifest.description} {' '.join(plugin.manifest.tags)}"
                if query.lower() not in search_text.lower():
                    continue
            
            results.append(plugin)
        
        # Sort by relevance (rating + downloads)
        results.sort(key=lambda p: (p.stats.average_rating * p.stats.downloads), reverse=True)
        
        return results[:limit]
    
    def get_featured_plugins(self) -> List[MarketplacePlugin]:
        """Get featured plugins from the marketplace."""
        self._refresh_cache_if_needed()
        
        featured = []
        for plugin_name in self.featured_plugins:
            if plugin_name in self.local_plugins:
                plugin = self.local_plugins[plugin_name]
                if plugin.featured:
                    featured.append(plugin)
        
        return featured
    
    def get_plugin_details(self, plugin_name: str) -> Optional[MarketplacePlugin]:
        """Get detailed information about a specific plugin."""
        self._refresh_cache_if_needed()
        return self.local_plugins.get(plugin_name)
    
    def submit_rating(self, plugin_name: str, rating: float, review: str, 
                     user_id: str) -> bool:
        """Submit a rating and review for a plugin."""
        if not (1.0 <= rating <= 5.0):
            raise FlashGenieError("Rating must be between 1.0 and 5.0")
        
        if plugin_name not in self.local_plugins:
            raise FlashGenieError(f"Plugin not found: {plugin_name}")
        
        # Create rating
        plugin_rating = PluginRating(
            user_id=user_id,
            rating=rating,
            review=review,
            date=datetime.now()
        )
        
        # Add to plugin
        plugin = self.local_plugins[plugin_name]
        
        # Remove existing rating from same user
        plugin.ratings = [r for r in plugin.ratings if r.user_id != user_id]
        plugin.ratings.append(plugin_rating)
        
        # Update stats
        self._update_plugin_stats(plugin)
        
        # Save to cache
        self._save_cache()
        
        self.logger.info(f"Rating submitted for {plugin_name}: {rating}/5.0")
        return True
    
    def download_plugin(self, plugin_name: str, target_dir: Path) -> Path:
        """Download a plugin from the marketplace."""
        plugin = self.get_plugin_details(plugin_name)
        if not plugin:
            raise FlashGenieError(f"Plugin not found: {plugin_name}")
        
        # In a real implementation, this would download from the marketplace
        # For now, we'll simulate by creating a package
        self.logger.info(f"Downloading plugin: {plugin_name}")
        
        # Update download stats
        plugin.stats.downloads += 1
        self._save_cache()
        
        # Return simulated download path
        download_path = target_dir / f"{plugin_name}-{plugin.manifest.version}.zip"
        return download_path
    
    def publish_plugin(self, plugin_path: Path, 
                      categories: List[MarketplaceCategory],
                      screenshots: List[str] = None,
                      price: float = 0.0) -> bool:
        """Publish a plugin to the marketplace."""
        # Load plugin manifest
        manifest_file = plugin_path / "plugin.json"
        if not manifest_file.exists():
            raise FlashGenieError("Plugin manifest not found")
        
        with open(manifest_file, 'r') as f:
            manifest_data = json.load(f)
        
        manifest = PluginManifest.from_dict(manifest_data)
        
        # Create marketplace plugin
        marketplace_plugin = MarketplacePlugin(
            manifest=manifest,
            stats=PluginStats(),
            categories=categories,
            screenshots=screenshots or [],
            price=price
        )
        
        # Add to local registry (in real implementation, would upload to server)
        self.local_plugins[manifest.name] = marketplace_plugin
        
        # Save cache
        self._save_cache()
        
        self.logger.info(f"Plugin published: {manifest.name}")
        return True
    
    def get_plugin_recommendations(self, user_plugins: List[str]) -> List[MarketplacePlugin]:
        """Get plugin recommendations based on user's installed plugins."""
        self._refresh_cache_if_needed()
        
        # Simple recommendation algorithm
        recommendations = []
        user_types = set()
        user_tags = set()
        
        # Analyze user's plugins
        for plugin_name in user_plugins:
            if plugin_name in self.local_plugins:
                plugin = self.local_plugins[plugin_name]
                user_types.add(plugin.manifest.plugin_type)
                user_tags.update(plugin.manifest.tags)
        
        # Find similar plugins
        for plugin in self.local_plugins.values():
            if plugin.manifest.name in user_plugins:
                continue
            
            # Score based on type and tag similarity
            score = 0
            if plugin.manifest.plugin_type in user_types:
                score += 2
            
            tag_overlap = len(set(plugin.manifest.tags) & user_tags)
            score += tag_overlap
            
            # Boost popular plugins
            score += plugin.stats.average_rating
            
            if score > 2:
                recommendations.append((plugin, score))
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [plugin for plugin, score in recommendations[:10]]
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get overall marketplace statistics."""
        self._refresh_cache_if_needed()
        
        total_plugins = len(self.local_plugins)
        total_downloads = sum(p.stats.downloads for p in self.local_plugins.values())
        avg_rating = sum(p.stats.average_rating for p in self.local_plugins.values()) / total_plugins if total_plugins > 0 else 0.0
        
        # Count by type
        type_counts = {}
        for plugin in self.local_plugins.values():
            plugin_type = plugin.manifest.plugin_type.value
            type_counts[plugin_type] = type_counts.get(plugin_type, 0) + 1
        
        return {
            "total_plugins": total_plugins,
            "total_downloads": total_downloads,
            "average_rating": round(avg_rating, 2),
            "plugin_types": type_counts,
            "featured_count": len(self.featured_plugins),
            "free_plugins": sum(1 for p in self.local_plugins.values() if p.price == 0.0),
            "paid_plugins": sum(1 for p in self.local_plugins.values() if p.price > 0.0)
        }
    
    def _refresh_cache_if_needed(self) -> None:
        """Refresh marketplace cache if it's stale."""
        cache_file = self.cache_dir / "marketplace_cache.json"
        
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.cache_duration:
                return
        
        # In a real implementation, this would fetch from the marketplace API
        self._populate_sample_data()
        self._save_cache()
    
    def _load_cache(self) -> None:
        """Load marketplace data from cache."""
        cache_file = self.cache_dir / "marketplace_cache.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # Load plugins
                for plugin_data in data.get("plugins", []):
                    manifest_data = plugin_data["manifest"]
                    manifest = PluginManifest.from_dict(manifest_data)
                    
                    stats_data = plugin_data["stats"]
                    stats = PluginStats(
                        downloads=stats_data["downloads"],
                        active_users=stats_data["active_users"],
                        average_rating=stats_data["average_rating"],
                        total_ratings=stats_data["total_ratings"],
                        last_updated=datetime.fromisoformat(stats_data["last_updated"]),
                        compatibility_score=stats_data.get("compatibility_score", 1.0),
                        security_score=stats_data.get("security_score", 1.0)
                    )
                    
                    # Load ratings
                    ratings = []
                    for rating_data in plugin_data.get("ratings", []):
                        rating = PluginRating(
                            user_id=rating_data["user_id"],
                            rating=rating_data["rating"],
                            review=rating_data["review"],
                            date=datetime.fromisoformat(rating_data["date"]),
                            helpful_votes=rating_data.get("helpful_votes", 0),
                            verified_purchase=rating_data.get("verified_purchase", False)
                        )
                        ratings.append(rating)
                    
                    # Create marketplace plugin
                    categories = [MarketplaceCategory(cat) for cat in plugin_data.get("categories", [])]
                    
                    marketplace_plugin = MarketplacePlugin(
                        manifest=manifest,
                        stats=stats,
                        ratings=ratings,
                        categories=categories,
                        screenshots=plugin_data.get("screenshots", []),
                        changelog=plugin_data.get("changelog", ""),
                        price=plugin_data.get("price", 0.0),
                        license_type=plugin_data.get("license_type", "MIT"),
                        support_url=plugin_data.get("support_url"),
                        documentation_url=plugin_data.get("documentation_url"),
                        verified=plugin_data.get("verified", False),
                        featured=plugin_data.get("featured", False)
                    )
                    
                    self.local_plugins[manifest.name] = marketplace_plugin
                
                # Load featured plugins
                self.featured_plugins = data.get("featured_plugins", [])
                
            except Exception as e:
                self.logger.warning(f"Failed to load marketplace cache: {e}")
                self._populate_sample_data()
        else:
            self._populate_sample_data()
    
    def _save_cache(self) -> None:
        """Save marketplace data to cache."""
        cache_file = self.cache_dir / "marketplace_cache.json"
        
        data = {
            "plugins": [],
            "featured_plugins": self.featured_plugins,
            "last_updated": datetime.now().isoformat()
        }
        
        for plugin in self.local_plugins.values():
            plugin_data = {
                "manifest": {
                    "name": plugin.manifest.name,
                    "version": plugin.manifest.version,
                    "description": plugin.manifest.description,
                    "author": plugin.manifest.author,
                    "license": plugin.manifest.license,
                    "flashgenie_version": plugin.manifest.flashgenie_version,
                    "type": plugin.manifest.plugin_type.value,
                    "entry_point": plugin.manifest.entry_point,
                    "permissions": [p.value for p in plugin.manifest.permissions],
                    "dependencies": plugin.manifest.dependencies,
                    "settings_schema": plugin.manifest.settings_schema,
                    "homepage": plugin.manifest.homepage,
                    "repository": plugin.manifest.repository,
                    "tags": plugin.manifest.tags
                },
                "stats": {
                    "downloads": plugin.stats.downloads,
                    "active_users": plugin.stats.active_users,
                    "average_rating": plugin.stats.average_rating,
                    "total_ratings": plugin.stats.total_ratings,
                    "last_updated": plugin.stats.last_updated.isoformat(),
                    "compatibility_score": plugin.stats.compatibility_score,
                    "security_score": plugin.stats.security_score
                },
                "ratings": [
                    {
                        "user_id": rating.user_id,
                        "rating": rating.rating,
                        "review": rating.review,
                        "date": rating.date.isoformat(),
                        "helpful_votes": rating.helpful_votes,
                        "verified_purchase": rating.verified_purchase
                    }
                    for rating in plugin.ratings
                ],
                "categories": [cat.value for cat in plugin.categories],
                "screenshots": plugin.screenshots,
                "changelog": plugin.changelog,
                "price": plugin.price,
                "license_type": plugin.license_type,
                "support_url": plugin.support_url,
                "documentation_url": plugin.documentation_url,
                "verified": plugin.verified,
                "featured": plugin.featured
            }
            data["plugins"].append(plugin_data)
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_plugin_stats(self, plugin: MarketplacePlugin) -> None:
        """Update plugin statistics based on ratings."""
        if plugin.ratings:
            total_rating = sum(r.rating for r in plugin.ratings)
            plugin.stats.average_rating = total_rating / len(plugin.ratings)
            plugin.stats.total_ratings = len(plugin.ratings)
        else:
            plugin.stats.average_rating = 0.0
            plugin.stats.total_ratings = 0
    
    def _populate_sample_data(self) -> None:
        """Populate sample marketplace data for demonstration."""
        # This would be replaced with actual API calls in production
        sample_plugins = [
            {
                "name": "dark-theme",
                "type": PluginType.THEME,
                "description": "Professional dark theme for FlashGenie",
                "author": "FlashGenie Team",
                "downloads": 1250,
                "rating": 4.8,
                "categories": [MarketplaceCategory.OFFICIAL, MarketplaceCategory.POPULAR],
                "featured": True
            },
            {
                "name": "ai-content-generator", 
                "type": PluginType.AI_ENHANCEMENT,
                "description": "AI-powered flashcard generation",
                "author": "FlashGenie Team",
                "downloads": 890,
                "rating": 4.6,
                "categories": [MarketplaceCategory.OFFICIAL, MarketplaceCategory.FEATURED],
                "featured": True
            },
            {
                "name": "voice-integration",
                "type": PluginType.QUIZ_MODE,
                "description": "Voice learning with TTS and STT",
                "author": "FlashGenie Team", 
                "downloads": 567,
                "rating": 4.4,
                "categories": [MarketplaceCategory.OFFICIAL, MarketplaceCategory.ACCESSIBILITY],
                "featured": False
            }
        ]
        
        for plugin_data in sample_plugins:
            # Create manifest
            manifest = PluginManifest(
                name=plugin_data["name"],
                version="1.0.0",
                description=plugin_data["description"],
                author=plugin_data["author"],
                license="MIT",
                flashgenie_version=">=1.8.0",
                plugin_type=plugin_data["type"],
                entry_point=f"{plugin_data['name'].replace('-', '_')}.Plugin",
                permissions=[],
                dependencies=[],
                settings_schema={},
                homepage=f"https://github.com/flashgenie/{plugin_data['name']}",
                repository=f"https://github.com/flashgenie/{plugin_data['name']}",
                tags=[plugin_data["type"].value, "official"]
            )
            
            # Create stats
            stats = PluginStats(
                downloads=plugin_data["downloads"],
                active_users=plugin_data["downloads"] // 2,
                average_rating=plugin_data["rating"],
                total_ratings=plugin_data["downloads"] // 10,
                last_updated=datetime.now() - timedelta(days=7)
            )
            
            # Create marketplace plugin
            marketplace_plugin = MarketplacePlugin(
                manifest=manifest,
                stats=stats,
                categories=plugin_data["categories"],
                verified=True,
                featured=plugin_data["featured"]
            )
            
            self.local_plugins[manifest.name] = marketplace_plugin
            
            if plugin_data["featured"]:
                self.featured_plugins.append(manifest.name)
