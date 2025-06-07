"""
Plugin command handlers for FlashGenie CLI.

This module contains handlers for plugin management, development kit, and marketplace operations.
"""

import sys
from pathlib import Path
from flashgenie.utils.exceptions import FlashGenieError


def handle_plugins_command(args) -> None:
    """Handle the plugins command."""
    from flashgenie.core.plugin_manager import PluginManager
    
    try:
        plugin_manager = PluginManager()
        
        if args.action == 'list':
            _handle_plugins_list(plugin_manager)
        elif args.action == 'discover':
            _handle_plugins_discover(plugin_manager)
        elif args.action == 'enable':
            _handle_plugins_enable(plugin_manager, args.name)
        elif args.action == 'disable':
            _handle_plugins_disable(plugin_manager, args.name)
        elif args.action == 'install':
            _handle_plugins_install(plugin_manager, args.path, args.category)
        elif args.action == 'uninstall':
            _handle_plugins_uninstall(plugin_manager, args.name)
        elif args.action == 'info':
            _handle_plugins_info(plugin_manager, args.name)
        else:
            print(f"Unknown plugins action: {args.action}")
            print("Available actions: list, discover, enable, disable, install, uninstall, info")
            sys.exit(1)
            
    except FlashGenieError as e:
        print(f"Plugin operation failed: {e}")
        sys.exit(1)


def _handle_plugins_list(plugin_manager):
    """Handle plugins list command."""
    plugins = plugin_manager.list_plugins()
    
    if not plugins:
        print("No plugins found. Use 'plugins discover' to scan for plugins.")
        return
    
    print("🔌 **FlashGenie Plugins**")
    print("=" * 50)
    
    # Group by status
    status_groups = {}
    for plugin in plugins:
        status = plugin.status.value
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(plugin)
    
    for status, plugin_list in status_groups.items():
        status_emoji = {
            'enabled': '✅',
            'installed': '📦',
            'disabled': '⏸️',
            'error': '❌'
        }.get(status, '❓')
        
        print(f"\n{status_emoji} **{status.upper()}** ({len(plugin_list)}):")
        for plugin in plugin_list:
            manifest = plugin.manifest
            print(f"   • {manifest.name} v{manifest.version}")
            print(f"     {manifest.description}")
            print(f"     Type: {manifest.plugin_type.value} | Author: {manifest.author}")
            if plugin.error_message:
                print(f"     Error: {plugin.error_message}")
            print()


def _handle_plugins_discover(plugin_manager):
    """Handle plugins discover command."""
    print("🔍 Discovering plugins...")
    discovered = plugin_manager.discover_plugins()
    print(f"Found {len(discovered)} plugins: {', '.join(discovered)}")


def _handle_plugins_enable(plugin_manager, plugin_name):
    """Handle plugins enable command."""
    if not plugin_name:
        print("Error: Plugin name required for enable action")
        sys.exit(1)
    
    print(f"🔌 Enabling plugin '{plugin_name}'...")
    if plugin_manager.enable_plugin(plugin_name):
        print(f"✅ Plugin '{plugin_name}' enabled successfully")
    else:
        print(f"❌ Failed to enable plugin '{plugin_name}'")
        sys.exit(1)


def _handle_plugins_disable(plugin_manager, plugin_name):
    """Handle plugins disable command."""
    if not plugin_name:
        print("Error: Plugin name required for disable action")
        sys.exit(1)
    
    print(f"⏸️ Disabling plugin '{plugin_name}'...")
    if plugin_manager.disable_plugin(plugin_name):
        print(f"✅ Plugin '{plugin_name}' disabled successfully")
    else:
        print(f"❌ Failed to disable plugin '{plugin_name}'")
        sys.exit(1)


def _handle_plugins_install(plugin_manager, plugin_path, category):
    """Handle plugins install command."""
    if not plugin_path:
        print("Error: Plugin path required for install action")
        sys.exit(1)
    
    path = Path(plugin_path)
    if not path.exists():
        print(f"Error: Plugin path does not exist: {path}")
        sys.exit(1)
    
    print(f"📦 Installing plugin from '{path}'...")
    if plugin_manager.install_plugin(path, category):
        print(f"✅ Plugin installed successfully")
    else:
        print(f"❌ Failed to install plugin")
        sys.exit(1)


def _handle_plugins_uninstall(plugin_manager, plugin_name):
    """Handle plugins uninstall command."""
    if not plugin_name:
        print("Error: Plugin name required for uninstall action")
        sys.exit(1)
    
    print(f"🗑️ Uninstalling plugin '{plugin_name}'...")
    if plugin_manager.uninstall_plugin(plugin_name):
        print(f"✅ Plugin '{plugin_name}' uninstalled successfully")
    else:
        print(f"❌ Failed to uninstall plugin '{plugin_name}'")
        sys.exit(1)


def _handle_plugins_info(plugin_manager, plugin_name):
    """Handle plugins info command."""
    if not plugin_name:
        print("Error: Plugin name required for info action")
        sys.exit(1)
    
    plugins = plugin_manager.list_plugins()
    plugin_info = next((p for p in plugins if p.manifest.name == plugin_name), None)
    
    if not plugin_info:
        print(f"Error: Plugin '{plugin_name}' not found")
        sys.exit(1)
    
    manifest = plugin_info.manifest
    print(f"🔌 **Plugin Information: {manifest.name}**")
    print("=" * 50)
    print(f"Name: {manifest.name}")
    print(f"Version: {manifest.version}")
    print(f"Description: {manifest.description}")
    print(f"Author: {manifest.author}")
    print(f"License: {manifest.license}")
    print(f"Type: {manifest.plugin_type.value}")
    print(f"Status: {plugin_info.status.value}")
    print(f"FlashGenie Version: {manifest.flashgenie_version}")
    
    if manifest.permissions:
        print(f"\nPermissions:")
        for perm in manifest.permissions:
            desc = plugin_manager.security_manager.get_permission_description(perm)
            print(f"   • {perm.value}: {desc}")
    
    if manifest.dependencies:
        print(f"\nDependencies:")
        for dep in manifest.dependencies:
            print(f"   • {dep}")
    
    if manifest.homepage:
        print(f"\nHomepage: {manifest.homepage}")
    
    if manifest.repository:
        print(f"Repository: {manifest.repository}")
    
    if plugin_info.error_message:
        print(f"\nError: {plugin_info.error_message}")


def handle_pdk_command(args) -> None:
    """Handle the Plugin Development Kit command."""
    from flashgenie.core.plugin_dev_kit import PluginDevelopmentKit
    from flashgenie.core.plugin_system import PluginType
    
    try:
        pdk = PluginDevelopmentKit()
        
        if args.action == 'create':
            _handle_pdk_create(pdk, args)
        elif args.action == 'validate':
            _handle_pdk_validate(pdk, args.path)
        elif args.action == 'test':
            _handle_pdk_test(pdk, args.path, args.test_mode)
        elif args.action == 'package':
            _handle_pdk_package(pdk, args.path, args.output)
        else:
            print(f"Unknown PDK action: {args.action}")
            print("Available actions: create, validate, test, package")
            sys.exit(1)
            
    except FlashGenieError as e:
        print(f"PDK operation failed: {e}")
        sys.exit(1)


def _handle_pdk_create(pdk, args):
    """Handle PDK create command."""
    if not args.name:
        print("Error: Plugin name required for create action")
        sys.exit(1)
    
    if not args.type:
        print("Error: Plugin type required for create action")
        sys.exit(1)
    
    try:
        from flashgenie.core.plugin_system import PluginType
        plugin_type = PluginType(args.type)
    except ValueError:
        print(f"Error: Invalid plugin type: {args.type}")
        print(f"Available types: {', '.join([t.value for t in PluginType])}")
        sys.exit(1)
    
    print(f"🏗️ Creating {args.type} plugin: {args.name}")
    plugin_dir = pdk.create_plugin_scaffold(args.name, plugin_type, args.author)
    
    print(f"\n🎉 Plugin scaffold created successfully!")
    print(f"📁 Location: {plugin_dir}")
    print(f"\n📋 Next steps:")
    print(f"   1. Edit {plugin_dir}/plugin.json to configure your plugin")
    print(f"   2. Implement your plugin in {plugin_dir}/__init__.py")
    print(f"   3. Test your plugin: python -m flashgenie pdk test --path {plugin_dir}")
    print(f"   4. Package your plugin: python -m flashgenie pdk package --path {plugin_dir}")


def _handle_pdk_validate(pdk, plugin_path):
    """Handle PDK validate command."""
    if not plugin_path:
        print("Error: Plugin path required for validate action")
        sys.exit(1)
    
    path = Path(plugin_path)
    if not path.exists():
        print(f"Error: Plugin path does not exist: {path}")
        sys.exit(1)
    
    print(f"🔍 Validating plugin: {path}")
    results = pdk.validate_plugin(path)
    
    if results["valid"]:
        print("✅ Plugin validation passed!")
    else:
        print("❌ Plugin validation failed!")
    
    if results["errors"]:
        print(f"\n🚨 Errors ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"   • {error}")
    
    if results["warnings"]:
        print(f"\n⚠️ Warnings ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"   • {warning}")
    
    if results["suggestions"]:
        print(f"\n💡 Suggestions ({len(results['suggestions'])}):")
        for suggestion in results["suggestions"]:
            print(f"   • {suggestion}")
    
    if not results["valid"]:
        sys.exit(1)


def _handle_pdk_test(pdk, plugin_path, test_mode):
    """Handle PDK test command."""
    if not plugin_path:
        print("Error: Plugin path required for test action")
        sys.exit(1)
    
    path = Path(plugin_path)
    if not path.exists():
        print(f"Error: Plugin path does not exist: {path}")
        sys.exit(1)
    
    print(f"🧪 Testing plugin: {path}")
    results = pdk.test_plugin(path, test_mode)
    
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {results['tests_run']}")
    print(f"   Tests passed: {results['tests_passed']}")
    print(f"   Tests failed: {results['tests_failed']}")
    
    if results["output"]:
        print(f"\n📝 Test Output:")
        for output in results["output"]:
            print(f"   {output}")
    
    if results["errors"]:
        print(f"\n🚨 Errors:")
        for error in results["errors"]:
            print(f"   • {error}")
    
    if results["success"]:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


def _handle_pdk_package(pdk, plugin_path, output_dir):
    """Handle PDK package command."""
    if not plugin_path:
        print("Error: Plugin path required for package action")
        sys.exit(1)
    
    path = Path(plugin_path)
    if not path.exists():
        print(f"Error: Plugin path does not exist: {path}")
        sys.exit(1)
    
    output = Path(output_dir) if output_dir else None
    
    print(f"📦 Packaging plugin: {path}")
    package_path = pdk.package_plugin(path, output)
    
    print(f"\n🎉 Plugin packaged successfully!")
    print(f"📁 Package location: {package_path}")
    print(f"\n📋 Installation instructions:")
    print(f"   python -m flashgenie plugins install {package_path}")


def handle_marketplace_command(args) -> None:
    """Handle the marketplace command."""
    from flashgenie.core.plugin_manager import PluginManager
    from flashgenie.core.plugin_system import PluginType
    
    try:
        plugin_manager = PluginManager()
        
        if args.action == 'search':
            _handle_marketplace_search(plugin_manager, args)
        elif args.action == 'featured':
            _handle_marketplace_featured(plugin_manager)
        elif args.action == 'install':
            _handle_marketplace_install(plugin_manager, args.name)
        elif args.action == 'rate':
            _handle_marketplace_rate(plugin_manager, args)
        elif args.action == 'recommendations':
            _handle_marketplace_recommendations(plugin_manager)
        elif args.action == 'stats':
            _handle_marketplace_stats(plugin_manager)
        else:
            print(f"Unknown marketplace action: {args.action}")
            print("Available actions: search, featured, install, rate, recommendations, stats")
            sys.exit(1)
            
    except FlashGenieError as e:
        print(f"Marketplace operation failed: {e}")
        sys.exit(1)


def _handle_marketplace_search(plugin_manager, args):
    """Handle marketplace search command."""
    query = args.query or ""
    filters = {}
    
    if args.type:
        try:
            from flashgenie.core.plugin_system import PluginType
            filters['plugin_type'] = PluginType(args.type)
        except ValueError:
            print(f"Error: Invalid plugin type: {args.type}")
            sys.exit(1)
    
    if args.free_only:
        filters['free_only'] = True
    
    if args.min_rating:
        filters['min_rating'] = args.min_rating
    
    print(f"🔍 Searching marketplace: '{query}'")
    results = plugin_manager.search_marketplace(query, **filters)
    
    if not results:
        print("No plugins found matching your criteria.")
        return
    
    print(f"\n📦 **Found {len(results)} plugins:**")
    print("=" * 60)
    
    for plugin in results:
        price_str = "Free" if plugin.price == 0.0 else f"${plugin.price:.2f}"
        rating_str = f"⭐ {plugin.stats.average_rating:.1f}" if plugin.stats.total_ratings > 0 else "No ratings"
        verified_str = "✅ Verified" if plugin.verified else ""
        
        print(f"\n📌 **{plugin.manifest.name}** v{plugin.manifest.version}")
        print(f"   {plugin.manifest.description}")
        print(f"   Author: {plugin.manifest.author} | Type: {plugin.manifest.plugin_type.value}")
        print(f"   {rating_str} | Downloads: {plugin.stats.downloads} | {price_str} {verified_str}")
        
        if plugin.manifest.tags:
            print(f"   Tags: {', '.join(plugin.manifest.tags)}")


def _handle_marketplace_featured(plugin_manager):
    """Handle marketplace featured command."""
    print("🌟 **Featured Plugins**")
    print("=" * 50)
    
    featured = plugin_manager.get_featured_plugins()
    
    if not featured:
        print("No featured plugins available.")
        return
    
    for plugin in featured:
        print(f"\n⭐ **{plugin.manifest.name}** v{plugin.manifest.version}")
        print(f"   {plugin.manifest.description}")
        print(f"   Author: {plugin.manifest.author}")
        print(f"   Rating: ⭐ {plugin.stats.average_rating:.1f} | Downloads: {plugin.stats.downloads}")


def _handle_marketplace_install(plugin_manager, plugin_name):
    """Handle marketplace install command."""
    if not plugin_name:
        print("Error: Plugin name required for install action")
        sys.exit(1)
    
    print(f"📦 Installing plugin from marketplace: {plugin_name}")
    
    if plugin_manager.install_from_marketplace(plugin_name):
        print(f"✅ Successfully installed plugin: {plugin_name}")
        print(f"💡 Enable with: python -m flashgenie plugins enable {plugin_name}")
    else:
        print(f"❌ Failed to install plugin: {plugin_name}")
        sys.exit(1)


def _handle_marketplace_rate(plugin_manager, args):
    """Handle marketplace rate command."""
    if not all([args.name, args.rating, args.review, args.user_id]):
        print("Error: Plugin name, rating, review, and user-id required for rate action")
        sys.exit(1)
    
    if not (1.0 <= args.rating <= 5.0):
        print("Error: Rating must be between 1.0 and 5.0")
        sys.exit(1)
    
    print(f"⭐ Rating plugin: {args.name}")
    
    if plugin_manager.rate_plugin(args.name, args.rating, args.review, args.user_id):
        print(f"✅ Successfully rated plugin: {args.name} ({args.rating}/5.0)")
    else:
        print(f"❌ Failed to rate plugin: {args.name}")
        sys.exit(1)


def _handle_marketplace_recommendations(plugin_manager):
    """Handle marketplace recommendations command."""
    print("💡 **Plugin Recommendations**")
    print("=" * 50)
    
    recommendations = plugin_manager.get_plugin_recommendations()
    
    if not recommendations:
        print("No recommendations available. Install more plugins to get personalized recommendations.")
        return
    
    for plugin in recommendations:
        print(f"\n🎯 **{plugin.manifest.name}** v{plugin.manifest.version}")
        print(f"   {plugin.manifest.description}")
        print(f"   Type: {plugin.manifest.plugin_type.value} | Author: {plugin.manifest.author}")
        print(f"   Rating: ⭐ {plugin.stats.average_rating:.1f} | Downloads: {plugin.stats.downloads}")
        
        if plugin.manifest.tags:
            print(f"   Tags: {', '.join(plugin.manifest.tags)}")


def _handle_marketplace_stats(plugin_manager):
    """Handle marketplace stats command."""
    print("📊 **Marketplace Statistics**")
    print("=" * 50)
    
    stats = plugin_manager.marketplace.get_marketplace_stats()
    
    print(f"Total Plugins: {stats['total_plugins']}")
    print(f"Total Downloads: {stats['total_downloads']:,}")
    print(f"Average Rating: ⭐ {stats['average_rating']:.1f}")
    print(f"Featured Plugins: {stats['featured_count']}")
    print(f"Free Plugins: {stats['free_plugins']}")
    print(f"Paid Plugins: {stats['paid_plugins']}")
    
    print(f"\n📈 **Plugin Types:**")
    for plugin_type, count in stats['plugin_types'].items():
        print(f"   {plugin_type}: {count}")
