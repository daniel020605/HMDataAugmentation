class DependencyResolver:
    def __init__(self):
        self.resolved = set()
        self.being_resolved = set()
        self.dependency_graph = {}  # Track dependency relationships

    def get_item_id(self, item):
        """Create a unique hashable identifier for an item"""
        if isinstance(item, dict):
            item_type = item.get('type', '')
            item_name = item.get('name', '')
            item_file = item.get('file', '')  # Include file path for uniqueness
            return f"{item_type}:{item_name}:{item_file}"
        return id(item)

    def resolve(self, item, get_deps_func, analyze_deps_func, max_depth=None, current_depth=0):
        """
        Resolves dependencies for an item using topological sort, with an optional depth limit.
        """
        if max_depth is not None and current_depth >= max_depth:
            return  # Stop resolving if the maximum depth is reached

        item_id = self.get_item_id(item)
        self.dependency_graph[item_id] = set()

        # Skip resolution if the item is in the same file
        if item.get('file') == item.get('current_file'):
            return

        # Stop processing if the file is already in the dependency chain
        if item.get('file') in {dep.get('file') for dep in self.being_resolved if isinstance(dep, dict)}:
            return

        if item_id in self.being_resolved:
            path = self._find_cycle(item_id)
            raise CircularDependencyError(f"Circular dependency detected: {' -> '.join(path)}")
        if item_id in self.resolved:
            return

        self.being_resolved.add(item)

        try:
            # Get immediate dependencies
            deps = get_deps_func(item)

            # Record dependencies in graph
            for dep in deps:
                dep_id = self.get_item_id(dep)
                self.dependency_graph[item_id].add(dep_id)
                self.resolve(dep, get_deps_func, analyze_deps_func, max_depth, current_depth + 1)

            # Analyze and set dependencies
            analyze_deps_func(item)

        finally:
            self.being_resolved.remove(item)
            self.resolved.add(item_id)

    def _find_cycle(self, start_id):
        """Find and return the cycle path"""
        path = []
        current = start_id

        while current not in path:
            path.append(current)
            for dep_id in self.dependency_graph.get(current, set()):
                if dep_id in self.being_resolved:
                    current = dep_id
                    break
            else:
                break

        start_index = path.index(current)
        return path[start_index:]

class CircularDependencyError(Exception):
    pass