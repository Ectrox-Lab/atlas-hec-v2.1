//! Tokenizers for Code-DNA

/// Simple tokenizer trait
pub trait Tokenizer<T> {
    fn encode(&self, input: &str) -> Vec<T>;
    fn decode(&self, tokens: &[T]) -> String;
    fn vocab_size(&self) -> usize;
}

/// Byte-level tokenizer
pub struct ByteTokenizer;

impl ByteTokenizer {
    pub fn new() -> Self {
        Self
    }
}

impl Tokenizer<u8> for ByteTokenizer {
    fn encode(&self, input: &str) -> Vec<u8> {
        input.bytes().collect()
    }
    
    fn decode(&self, tokens: &[u8]) -> String {
        String::from_utf8_lossy(tokens).to_string()
    }
    
    fn vocab_size(&self) -> usize {
        256
    }
}

/// Whitespace tokenizer for code
pub struct WhitespaceTokenizer;

impl WhitespaceTokenizer {
    pub fn new() -> Self {
        Self
    }
}

impl Tokenizer<String> for WhitespaceTokenizer {
    fn encode(&self, input: &str) -> Vec<String> {
        input.split_whitespace().map(|s| s.to_string()).collect()
    }
    
    fn decode(&self, tokens: &[String]) -> String {
        tokens.join(" ")
    }
    
    fn vocab_size(&self) -> usize {
        10000 // Arbitrary limit
    }
}
