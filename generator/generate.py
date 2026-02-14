#!/usr/bin/env python3 

import xml.etree.ElementTree as ET
import os
import sys
from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class ClassDef:
    name: str
    extends: str = None
    fields: List[tuple] = field(default_factory=list)
    
    def add_field(self, field_type: str, field_name: str, is_list: bool = False):
        if not any(f[1] == field_name for f in self.fields):
            self.fields.append((field_type, field_name, is_list))


@dataclass
class Edge:
    source_id: str
    target_id: str
    label: str = ""
    style: str = ""


class DrawIOParser:
    
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()
        self.id_to_class: Dict[str, str] = {}
        self.edges: List[Edge] = []
    
    @staticmethod
    def sanitize_class_name(name: str) -> str:
        parts = name.split()
        if len(parts) > 1:
            return ''.join(word.capitalize() for word in parts)
        else:
            return name[0].upper() + name[1:] if name else ""
    
    def parse(self):
        cells = self.root.findall('.//mxCell')
        text_labels = {}
        boxes = []
        
        for cell in cells:
            cell_id = cell.get('id')
            value = cell.get('value', '')
            style = cell.get('style', '')
            
            geometry = cell.find('mxGeometry')
            if geometry is not None:
                source = cell.get('source')
                target = cell.get('target')
                
                if source is None and target is None:
                    x = float(geometry.get('x', 0))
                    y = float(geometry.get('y', 0))
                    width = float(geometry.get('width', 0))
                    height = float(geometry.get('height', 0))
                    
                    if 'text;' in style and value.strip():
                        text_labels[(x, y)] = value.strip()
                    elif 'whiteSpace=wrap' in style:
                        boxes.append((cell_id, x, y, width, height, value.strip()))
        
        for cell_id, bx, by, bw, bh, value in boxes:
            class_name = value if value else None
            
            if not class_name:
                for (tx, ty), text in text_labels.items():
                    if bx <= tx <= bx + bw and by <= ty <= by + bh:
                        class_name = text
                        break
            
            if class_name:
                class_name = self.sanitize_class_name(class_name)
                self.id_to_class[cell_id] = class_name
        
        for cell in cells:
            source = cell.get('source')
            target = cell.get('target')
            
            if source and target:
                label = cell.get('value', '').strip()
                style = cell.get('style', '')
                self.edges.append(Edge(source_id=source, target_id=target, label=label, style=style))
    
    def get_classes(self) -> Set[str]:
        return set(self.id_to_class.values())
    
    def get_edges(self) -> List[Edge]:
        return self.edges


class RelationshipClassifier:
    
    @staticmethod
    def classify(edge: Edge) -> str:
        label_lower = edge.label.lower()
        style_lower = edge.style.lower()
        
        if 'expands' in label_lower:
            return 'EXPANDS'
        if 'depends' in label_lower:
            return 'DEPENDS'
        
        if 'endfill' in style_lower or 'startfill=1' in style_lower:
            if 'endfill=1' in style_lower or 'startarrow=oval' in style_lower:
                return 'HAVE'
        
        if 'dashed=1' in style_lower:
            if 'endarrow=open' in style_lower or 'endarrow=block' in style_lower:
                return 'EXPANDS'
            if 'endarrow=classic' in style_lower:
                return 'DEPENDS'
        
        if 'endarrow' in style_lower and 'dashed' not in style_lower:
            if 'endarrow=classic' in style_lower or 'endarrow=block' in style_lower:
                return 'PART_OF'
        
        return 'UNKNOWN'
    
    @staticmethod
    def get_multiplicity(edge: Edge) -> str:
        if '*' in edge.label:
            return '*'
        return '1'
    
    @staticmethod
    def has_black_circle(edge: Edge) -> bool:
        style = edge.style.lower()
        return 'startarrow=oval' in style or 'endarrow=oval' in style


class JavaGenerator:
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, classes: Dict[str, ClassDef]):
        for class_name, class_def in classes.items():
            self._generate_class(class_def)
    
    def _generate_class(self, class_def: ClassDef):
        lines = []
        
        if class_def.extends:
            lines.append(f"public class {class_def.name} extends {class_def.extends} {{")
        else:
            lines.append(f"public class {class_def.name} {{")
        
        lines.append("")
        
        if class_def.fields:
            for field_type, field_name, is_list in class_def.fields:
                if is_list:
                    lines.append(f"    private List<{field_type}> {field_name};")
                else:
                    lines.append(f"    private {field_type} {field_name};")
            lines.append("")
        
        lines.append(f"    public {class_def.name}() {{")
        for field_type, field_name, is_list in class_def.fields:
            if is_list:
                lines.append(f"        this.{field_name} = new ArrayList<>();")
        lines.append("    }")
        lines.append("")
        
        if class_def.fields:
            for field_type, field_name, is_list in class_def.fields:
                if is_list:
                    lines.append(f"    public List<{field_type}> get{self._capitalize(field_name)}() {{")
                    lines.append(f"        return {field_name};")
                else:
                    lines.append(f"    public {field_type} get{self._capitalize(field_name)}() {{")
                    lines.append(f"        return {field_name};")
                lines.append("    }")
                lines.append("")
                
                if is_list:
                    lines.append(f"    public void set{self._capitalize(field_name)}(List<{field_type}> {field_name}) {{")
                else:
                    lines.append(f"    public void set{self._capitalize(field_name)}({field_type} {field_name}) {{")
                lines.append(f"        this.{field_name} = {field_name};")
                lines.append("    }")
                lines.append("")
        
        lines.append("}")
        
        imports = []
        if any(is_list for _, _, is_list in class_def.fields):
            imports.append("import java.util.List;")
            imports.append("import java.util.ArrayList;")
        
        if imports:
            content = "\n".join(imports) + "\n\n" + "\n".join(lines)
        else:
            content = "\n".join(lines)
        
        file_path = os.path.join(self.output_dir, f"{class_def.name}.java")
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Generated: {file_path}")
    
    @staticmethod
    def _capitalize(name: str) -> str:
        return name[0].upper() + name[1:] if name else ""


class CodeGenerator:
    
    def __init__(self, xml_path: str, output_dir: str):
        self.xml_path = xml_path
        self.output_dir = output_dir
        self.parser = DrawIOParser(xml_path)
        self.classes: Dict[str, ClassDef] = {}
    
    def generate(self):
        print(f"Parsing model: {self.xml_path}")
        
        self.parser.parse()
        
        for class_name in self.parser.get_classes():
            self.classes[class_name] = ClassDef(name=class_name)
        
        print(f"Found {len(self.classes)} classes: {', '.join(self.classes.keys())}")
        
        print(f"Processing {len(self.parser.get_edges())} relationships...")
        for edge in self.parser.get_edges():
            self._process_relationship(edge)
        
        print(f"Generating Java files to: {self.output_dir}")
        generator = JavaGenerator(self.output_dir)
        generator.generate(self.classes)
        
        print("Generation complete!")
    
    def _process_relationship(self, edge: Edge):
        source_class = self.parser.id_to_class.get(edge.source_id)
        target_class = self.parser.id_to_class.get(edge.target_id)
        
        if not source_class or not target_class:
            return
        
        rel_type = RelationshipClassifier.classify(edge)
        multiplicity = RelationshipClassifier.get_multiplicity(edge)
        
        print(f"  {source_class} --[{rel_type}]--> {target_class} (multiplicity: {multiplicity})")
        
        if rel_type == 'EXPANDS':
            self.classes[source_class].extends = target_class
        
        elif rel_type == 'DEPENDS':
            field_name = target_class[0].lower() + target_class[1:]
            self.classes[source_class].add_field(target_class, field_name, False)
        
        elif rel_type == 'HAVE':
            is_list = (multiplicity == '*')
            field_name = target_class[0].lower() + target_class[1:]
            if is_list:
                field_name = field_name + 's'
            self.classes[source_class].add_field(target_class, field_name, is_list)
        
        elif rel_type == 'PART_OF':
            is_list = (multiplicity == '*')
            field_name = source_class[0].lower() + source_class[1:]
            if is_list:
                field_name = field_name + 's'
            self.classes[target_class].add_field(source_class, field_name, is_list)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate.py <input.xml> <output_dir>")
        print("Example: python generate.py model/diagram.xml src-gen/")
        sys.exit(1)
    
    xml_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(xml_path):
        print(f"Error: Input file not found: {xml_path}")
        sys.exit(1)
    
    generator = CodeGenerator(xml_path, output_dir)
    generator.generate()


if __name__ == '__main__':
    main()
