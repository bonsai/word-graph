use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Node {
    pub id: String,
    #[serde(rename = "type")]
    pub node_type: String,
    pub label: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub reading: Option<String>,
    #[serde(default)]
    pub metadata: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Provenance {
    pub source: String,
    pub method: String,
    pub version: String,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Edge {
    pub source: String,
    pub target: String,
    #[serde(rename = "type")]
    pub edge_type: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub score: Option<f64>,
    #[serde(default)]
    pub metadata: serde_json::Value,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub provenance: Option<Provenance>,
}

#[derive(Debug, Default)]
pub struct Graph {
    nodes: HashMap<String, Node>,
    edges: Vec<Edge>,
}

impl Graph {
    pub fn new() -> Self { Self::default() }

    pub fn add_node(&mut self, node: Node) {
        self.nodes.insert(node.id.clone(), node);
    }

    pub fn add_edge(&mut self, edge: Edge) {
        self.edges.push(edge);
    }

    pub fn node(&self, id: &str) -> Option<&Node> { self.nodes.get(id) }

    pub fn neighbors(&self, id: &str, edge_type: Option<&str>, limit: usize) -> Vec<&Node> {
        let mut seen = HashSet::new();
        let mut queue = VecDeque::new();
        let mut result = Vec::new();
        queue.push_back(id.to_owned());

        while let Some(current) = queue.pop_front() {
            for edge in self.edges.iter().filter(|e| {
                e.source == current && edge_type.map_or(true, |t| e.edge_type == t)
            }) {
                if seen.insert(edge.target.clone()) {
                    if let Some(node) = self.nodes.get(&edge.target) {
                        result.push(node);
                        if result.len() >= limit { return result; }
                    }
                    queue.push_back(edge.target.clone());
                }
            }
        }
        result
    }

    pub fn edges(&self) -> &[Edge] { &self.edges }
    pub fn nodes(&self) -> impl Iterator<Item = &Node> { self.nodes.values() }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn node(id: &str, label: &str) -> Node {
        Node { id: id.into(), node_type: "word".into(), label: label.into(), reading: None, metadata: serde_json::json!({}) }
    }

    #[test]
    fn traverses_phonetic_neighbors() {
        let mut graph = Graph::new();
        graph.add_node(node("station:nippori", "日暮里"));
        graph.add_node(node("word:shippori", "しっぽり"));
        graph.add_edge(Edge {
            source: "station:nippori".into(), target: "word:shippori".into(), edge_type: "phonetic".into(),
            score: Some(0.92), metadata: serde_json::json!({}), provenance: None,
        });
        let result = graph.neighbors("station:nippori", Some("phonetic"), 10);
        assert_eq!(result[0].label, "しっぽり");
    }
}
