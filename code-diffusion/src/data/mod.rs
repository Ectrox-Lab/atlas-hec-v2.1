use ndarray::{Array1, Array2, Array3};

pub mod tokenizer;
pub use tokenizer::*;

/// Token types for Edit-DNA
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum EditToken {
    // Structural operations
    AddIf = 0,
    AddElse,
    AddLoop,
    AddMatch,
    
    // Removal operations  
    RemoveCall,
    RemoveBranch,
    
    // Modification operations
    ChangeConst,
    ChangeVar,
    ChangeType,
    
    // Safety/Error handling
    InsertGuard,
    WrapTry,
    AddTimeout,
    AddAssert,
    
    // Resource management
    MoveAlloc,
    FreeResource,
    ReduceRetry,
    
    // Context markers
    ContextBefore,
    ContextAfter,
    Padding,
    
    // Special
    Unknown = 255,
}

impl EditToken {
    pub fn num_tokens() -> usize {
        20 // Number of defined tokens above
    }
    
    pub fn to_onehot(&self) -> Array1<f64> {
        let mut arr = Array1::zeros(Self::num_tokens());
        arr[*self as usize] = 1.0;
        arr
    }
}

/// Edit-DNA representation
#[derive(Debug, Clone)]
pub struct EditDNA {
    pub tokens: Vec<EditToken>,
    pub condition: PatchCategory,
}

impl EditDNA {
    pub const SEQ_LEN: usize = 64;
    pub const NUM_CHANNELS: usize = 1;
    
    pub fn new(tokens: Vec<EditToken>, condition: PatchCategory) -> Self {
        let mut dna = Self { tokens, condition };
        dna.pad();
        dna
    }
    
    fn pad(&mut self) {
        if self.tokens.len() < Self::SEQ_LEN {
            self.tokens.resize(Self::SEQ_LEN, EditToken::Padding);
        } else if self.tokens.len() > Self::SEQ_LEN {
            self.tokens.truncate(Self::SEQ_LEN);
        }
    }
    
    /// Convert to tensor representation (channels, seq_len)
    pub fn to_tensor(&self) -> Array2<f64> {
        let mut arr = Array2::zeros((Self::NUM_CHANNELS, Self::SEQ_LEN));
        for (i, token) in self.tokens.iter().enumerate() {
            arr[[0, i]] = *token as usize as f64;
        }
        // Normalize to [-1, 1]
        arr.mapv(|v| (v / EditToken::num_tokens() as f64) * 2.0 - 1.0)
    }
    
    /// Convert from tensor
    pub fn from_tensor(tensor: &Array2<f64>, condition: PatchCategory) -> Self {
        let tokens: Vec<EditToken> = tensor.row(0).iter()
            .map(|&v| {
                let idx = ((v + 1.0) / 2.0 * EditToken::num_tokens() as f64) as usize;
                match idx {
                    0 => EditToken::AddIf,
                    1 => EditToken::AddElse,
                    2 => EditToken::AddLoop,
                    3 => EditToken::AddMatch,
                    4 => EditToken::RemoveCall,
                    5 => EditToken::RemoveBranch,
                    6 => EditToken::ChangeConst,
                    7 => EditToken::ChangeVar,
                    8 => EditToken::ChangeType,
                    9 => EditToken::InsertGuard,
                    10 => EditToken::WrapTry,
                    11 => EditToken::AddTimeout,
                    12 => EditToken::AddAssert,
                    13 => EditToken::MoveAlloc,
                    14 => EditToken::FreeResource,
                    15 => EditToken::ReduceRetry,
                    16 => EditToken::ContextBefore,
                    17 => EditToken::ContextAfter,
                    18 => EditToken::Padding,
                    _ => EditToken::Unknown,
                }
            })
            .collect();
        
        Self::new(tokens, condition)
    }
}

/// Patch categories (condition labels)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PatchCategory {
    BugFix = 1,
    Performance,
    Memory,
    Safety,
    Refactor,
    IO,
    Concurrency,
}

impl PatchCategory {
    pub fn num_classes() -> usize {
        8 // Including 0 for unconditional
    }
    
    pub fn to_tensor(&self) -> Array1<f64> {
        Array1::from_elem(1, *self as usize as f64)
    }
}

/// Code-DNA encoder trait
pub trait CodeDNAEncoder {
    type Token;
    
    fn encode(&self, code: &str) -> Vec<Self::Token>;
    fn decode(&self, tokens: &[Self::Token]) -> String;
    fn to_tensor(&self, tokens: &[Self::Token]) -> Array3<f64>;
}

/// Simple tokenizer for Edit-DNA
pub struct EditTokenizer;

impl EditTokenizer {
    pub fn new() -> Self {
        Self
    }
    
    /// Parse a code diff and extract edit tokens
    pub fn tokenize_diff(&self, diff: &str) -> Vec<EditToken> {
        let mut tokens = vec![];
        
        for line in diff.lines() {
            if line.starts_with("+") {
                if line.contains("if ") {
                    tokens.push(EditToken::AddIf);
                } else if line.contains("loop") || line.contains("for ") || line.contains("while ") {
                    tokens.push(EditToken::AddLoop);
                } else if line.contains("match") || line.contains("switch") {
                    tokens.push(EditToken::AddMatch);
                } else if line.contains("try") || line.contains("catch") {
                    tokens.push(EditToken::WrapTry);
                } else if line.contains("guard") || line.contains("assert") {
                    tokens.push(EditToken::InsertGuard);
                } else if line.contains("timeout") {
                    tokens.push(EditToken::AddTimeout);
                } else if line.contains("alloc") || line.contains("new ") {
                    tokens.push(EditToken::MoveAlloc);
                }
            } else if line.starts_with("-") {
                if line.contains("(") && line.contains(")") {
                    tokens.push(EditToken::RemoveCall);
                }
            }
        }
        
        tokens
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_edit_dna() {
        let tokens = vec![EditToken::AddIf, EditToken::InsertGuard];
        let dna = EditDNA::new(tokens, PatchCategory::BugFix);
        assert_eq!(dna.tokens.len(), EditDNA::SEQ_LEN);
    }
    
    #[test]
    fn test_to_tensor() {
        let tokens = vec![EditToken::AddIf, EditToken::ChangeConst];
        let dna = EditDNA::new(tokens, PatchCategory::Performance);
        let tensor = dna.to_tensor();
        assert_eq!(tensor.shape(), &[1, 64]);
    }
}
