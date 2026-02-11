from typing import List, Dict, Set
import re
from collections import defaultdict, Counter
import random

class KnowledgeGraphBuilder:
    def __init__(self):
        """Initialize knowledge graph builder"""
        self.documents = {}
        self.entities = defaultdict(set)  # entity -> document_ids
        self.relationships = []  # (entity1, entity2, weight)
        self.entity_frequencies = Counter()
        
    def add_document(self, doc_id: str, text: str, chunks: List[str]):
        """Add a document and extract entities"""
        self.documents[doc_id] = {
            'text': text,
            'chunks': chunks,
            'entities': set()
        }
        
        # Extract entities (simplified - use NER in production)
        entities = self._extract_entities(text)
        
        for entity in entities:
            self.entities[entity].add(doc_id)
            self.documents[doc_id]['entities'].add(entity)
            self.entity_frequencies[entity] += 1
        
        # Build relationships
        self._build_relationships(entities)
    
    def _extract_entities(self, text: str) -> Set[str]:
        """Extract entities from text (simplified)"""
        # Remove common words
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their'
        }
        
        # Extract capitalized words and multi-word phrases
        entities = set()
        
        # Find capitalized sequences
        capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(capitalized_pattern, text)
        
        for match in matches:
            if match.lower() not in stopwords and len(match) > 2:
                entities.add(match)
        
        # Extract important terms (appears multiple times)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = Counter(words)
        
        for word, freq in word_freq.items():
            if freq >= 3 and word not in stopwords:
                entities.add(word.capitalize())
        
        return entities
    
    def _build_relationships(self, entities: List[str]):
        """Build relationships between entities"""
        # Entities that appear together in same document are related
        entities_list = list(entities)
        
        for i, entity1 in enumerate(entities_list):
            for entity2 in entities_list[i+1:]:
                # Check co-occurrence
                docs1 = self.entities[entity1]
                docs2 = self.entities[entity2]
                
                shared_docs = docs1 & docs2
                
                if shared_docs:
                    weight = len(shared_docs)
                    self.relationships.append((entity1, entity2, weight))
    
    def build_graph(self) -> Dict:
        """Build knowledge graph data for visualization"""
        # Select top entities
        top_entities = [
            entity for entity, _ in self.entity_frequencies.most_common(30)
        ]
        
        if not top_entities:
            return {
                'nodes': [],
                'edges': []
            }
        
        # Create nodes
        nodes = []
        entity_to_index = {}
        
        colors = [
            '#00d4ff',  # cyan
            '#ff00ff',  # magenta
            '#00ff88',  # green
            '#ffaa00',  # orange
            '#ff0080',  # pink
            '#00ffff',  # aqua
        ]
        
        for i, entity in enumerate(top_entities):
            entity_to_index[entity] = i
            
            # Calculate node size based on frequency
            freq = self.entity_frequencies[entity]
            size = 0.3 + (freq * 0.1)
            size = min(size, 1.5)  # Cap size
            
            # Assign type based on pattern
            if entity[0].isupper():
                entity_type = "Proper Noun"
            else:
                entity_type = "Concept"
            
            nodes.append({
                'id': i,
                'label': entity,
                'type': entity_type,
                'size': size,
                'color': colors[i % len(colors)],
                'connections': len([r for r in self.relationships if entity in (r[0], r[1])]),
                'frequency': freq
            })
        
        # Create edges
        edges = []
        added_edges = set()
        
        for entity1, entity2, weight in self.relationships:
            if entity1 in entity_to_index and entity2 in entity_to_index:
                idx1 = entity_to_index[entity1]
                idx2 = entity_to_index[entity2]
                
                edge_key = tuple(sorted([idx1, idx2]))
                
                if edge_key not in added_edges and weight >= 1:
                    edges.append({
                        'source': idx1,
                        'target': idx2,
                        'weight': weight
                    })
                    added_edges.add(edge_key)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_entities': len(self.entities),
            'total_documents': len(self.documents)
        }
    
    def get_node_count(self) -> int:
        """Get number of unique entities"""
        return len(self.entities)
    
    def get_entity_details(self, entity: str) -> Dict:
        """Get details about a specific entity"""
        if entity not in self.entities:
            return None
        
        doc_ids = self.entities[entity]
        
        # Find related entities
        related = []
        for e1, e2, weight in self.relationships:
            if e1 == entity:
                related.append({'entity': e2, 'weight': weight})
            elif e2 == entity:
                related.append({'entity': e1, 'weight': weight})
        
        related = sorted(related, key=lambda x: x['weight'], reverse=True)[:5]
        
        return {
            'entity': entity,
            'frequency': self.entity_frequencies[entity],
            'documents': list(doc_ids),
            'related_entities': related
        }
