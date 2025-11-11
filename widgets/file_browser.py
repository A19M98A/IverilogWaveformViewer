import os
from rich.text import Text
from textual.widgets import DirectoryTree
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode
from textual.worker import Worker


class NavigableDirectoryTree(DirectoryTree):
    """A DirectoryTree that adds a '..' entry to navigate up."""

    def _add_up_entry(self) -> None:
        """
        Adds a '..' navigation entry to the top of the tree if not in the root directory.
        This method is called after the directory contents have been loaded.
        """
        # Don't do anything if the tree is empty or we're at the root of the filesystem.
        if not self.root.children or os.path.abspath(self.path) == "/":
            return

        # Avoid adding a duplicate '..' entry.
        if self.root.children[0].data.name == "..":
            return

        # Create the data entry and the node for '..'.
        up_entry = DirEntry("..", os.path.join(self.path, ".."), True)
        up_node = self.root._add_node(up_entry)

        # Insert the '..' node at the beginning of the children list.
        self.root.children.insert(0, up_node)

        # Style the label with an icon and color.
        up_node.label = Text.from_markup("[bold blue]:arrow_up_small: ..[/]")

        # Refresh the tree view to show the new entry.
        self.root.refresh()

    def _load_directory(self, node: TreeNode) -> Worker:
        """
        Overrides the default directory loading to inject the '..' entry
        after the directory has been successfully loaded.
        """
        # Call the original method to get the Worker that loads the directory.
        load_worker = super()._load_directory(node)

        # The 'on_success' callback will be executed by the worker when it's done.
        def on_load_success():
            if node is self.root:
                self._add_up_entry()

        # Attach our callback to the worker.
        load_worker.on_success = on_load_success

        # It is CRITICAL to return the worker object.
        return load_worker


class FileBrowser(NavigableDirectoryTree):
    """The file browser widget using our navigable tree."""

    def __init__(self, path: str, *, id: str | None = None) -> None:
        super().__init__(path, id=id)
