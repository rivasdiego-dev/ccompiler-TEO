# parse_tree/parse_tree.py
from anytree import Node, RenderTree
from typing import Optional, Dict, List, Any
from lexer.token import Token
from lexer.token_type import TokenType

class ParseTree :
    def __init__(self):
        self.root: Optional[Node] = None
        self.current_node: Optional[Node] = None
        self.nodes: Dict[str, Node] = {}

    def __str__(self) -> str:
        """Representación en string del árbol"""
        if not self.root:
            return "Árbol vacío"
        
        return str(RenderTree(self.root))

    def create_node(self, name: str, parent: Optional[Node] = None, token: Optional[Token] = None) -> Node:
        """
        Crea un nuevo nodo en el árbol.
        Args:
            name: Nombre del nodo (regla gramatical o tipo de nodo)
            parent: Nodo padre (opcional)
            token: Token asociado al nodo (opcional)
        """
        node_name = f"{name} [{token.value}]" if token else name
        node = Node(node_name, parent=parent)
        self.nodes[id(node)] = node
        return node

    def set_root(self, name: str) -> None:
        """Establece el nodo raíz del árbol"""
        self.root = self.create_node(name)
        self.current_node = self.root

    def add_child(self, name: str, token: Optional[Token] = None) -> Node:
        """
        Añade un hijo al nodo actual y lo retorna.
        Args:
            name: Nombre del nodo hijo
            token: Token asociado al nodo (opcional)
        """
        if self.current_node is None:
            raise ValueError("No hay un nodo actual establecido")
        return self.create_node(name, parent=self.current_node, token=token)

    def move_to(self, node: Node) -> None:
        """Establece el nodo actual"""
        self.current_node = node

    def move_to_parent(self) -> None:
        """Mueve el nodo actual a su padre"""
        if self.current_node and self.current_node.parent:
            self.current_node = self.current_node.parent

    def visualize(self, filename: str) -> None:
        """
        Genera una visualización del árbol en un archivo de texto.
        Args:
            filename: Nombre del archivo donde se guardará la visualización
        """
        if not self.root:
            raise ValueError("El árbol está vacío")
        
        with open(filename, 'w', encoding='utf-8') as f:
            for pre, _, node in RenderTree(self.root):
                f.write(f"{pre}{node.name}\n")

    def get_tree(self) -> Optional[Node]:
        """Retorna el árbol completo"""
        return self.root