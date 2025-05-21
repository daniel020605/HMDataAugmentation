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
            return f"{item_type}:{item_name}"
        return id(item)

    def resolve(self, item, get_deps_func, analyze_deps_func):
        """
        Resolves dependencies for an item using topological sort
        """
        item_id = self.get_item_id(item)
        self.dependency_graph[item_id] = set()

        if item_id in self.being_resolved:
            path = self._find_cycle(item_id)
            raise CircularDependencyError(f"Circular dependency detected: {' -> '.join(path)}")
        if item_id in self.resolved:
            return

        self.being_resolved.add(item_id)

        try:
            # Get immediate dependencies
            deps = get_deps_func(item)

            # Record dependencies in graph
            for dep in deps:
                dep_id = self.get_item_id(dep)
                self.dependency_graph[item_id].add(dep_id)
                self.resolve(dep, get_deps_func, analyze_deps_func)

            # Analyze and set dependencies
            analyze_deps_func(item)

        finally:
            self.being_resolved.remove(item_id)
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