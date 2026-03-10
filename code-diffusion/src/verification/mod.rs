use crate::data::{EditDNA, EditToken};

/// Verification result
#[derive(Debug, Clone)]
pub struct VerificationResult {
    pub passed: bool,
    pub score: f64,
    pub checks: Vec<CheckResult>,
}

#[derive(Debug, Clone)]
pub struct CheckResult {
    pub name: String,
    pub passed: bool,
    pub score: f64,
    pub message: Option<String>,
}

impl VerificationResult {
    pub fn is_pass(&self) -> bool {
        self.passed
    }
    
    pub fn overall_score(&self) -> f64 {
        self.score
    }
}

/// Verifier for EditDNA -> Code
pub trait Verifier {
    fn verify(&self, dna: &EditDNA) -> VerificationResult;
}

/// Decoder: EditDNA -> Code/Patch
pub trait DNADecoder {
    fn decode(&self, dna: &EditDNA) -> String;
}

/// Simple patch decoder
pub struct PatchDecoder;

impl PatchDecoder {
    pub fn new() -> Self {
        Self
    }
}

impl DNADecoder for PatchDecoder {
    fn decode(&self, dna: &EditDNA) -> String {
        let mut patch = String::new();
        
        for token in &dna.tokens {
            match token {
                EditToken::AddIf => patch.push_str("+ if condition {\n"),
                EditToken::AddElse => patch.push_str("+ } else {\n"),
                EditToken::AddLoop => patch.push_str("+ for item in items {\n"),
                EditToken::AddMatch => patch.push_str("+ match value {\n"),
                EditToken::RemoveCall => patch.push_str("- old_call();\n"),
                EditToken::RemoveBranch => patch.push_str("- if old_condition {\n"),
                EditToken::ChangeConst => patch.push_str("~ const NEW_VALUE = 42;\n"),
                EditToken::ChangeVar => patch.push_str("~ let new_var = value;\n"),
                EditToken::InsertGuard => patch.push_str("+ if !condition { return; }\n"),
                EditToken::WrapTry => patch.push_str("+ try {\n"),
                EditToken::AddTimeout => patch.push_str("+ .timeout(Duration::from_secs(30))\n"),
                EditToken::AddAssert => patch.push_str("+ assert!(condition);\n"),
                EditToken::MoveAlloc => patch.push_str("~ let resource = acquire();\n"),
                EditToken::FreeResource => patch.push_str("+ drop(resource);\n"),
                EditToken::ReduceRetry => patch.push_str("~ retry_count -= 1;\n"),
                EditToken::ChangeType => patch.push_str("~ type NewType = OldType;\n"),
                EditToken::ContextBefore | EditToken::ContextAfter => {}
                EditToken::Padding => break,
                EditToken::Unknown => patch.push_str("? unknown\n"),
            }
        }
        
        patch
    }
}

/// Multi-stage verifier stack
pub struct VerifierStack {
    verifiers: Vec<Box<dyn Verifier>>,
    threshold: f64,
}

impl VerifierStack {
    pub fn new(threshold: f64) -> Self {
        Self {
            verifiers: vec![],
            threshold,
        }
    }
    
    pub fn add_verifier(&mut self, verifier: Box<dyn Verifier>) {
        self.verifiers.push(verifier);
    }
    
    pub fn verify(&self, dna: &EditDNA) -> VerificationResult {
        let mut all_passed = true;
        let mut total_score = 0.0;
        let mut checks = vec![];
        
        for verifier in &self.verifiers {
            let result = verifier.verify(dna);
            total_score += result.score;
            if !result.passed {
                all_passed = false;
            }
            checks.extend(result.checks);
        }
        
        let avg_score = if !self.verifiers.is_empty() {
            total_score / self.verifiers.len() as f64
        } else {
            0.0
        };
        
        VerificationResult {
            passed: all_passed && avg_score >= self.threshold,
            score: avg_score,
            checks,
        }
    }
}

/// Syntax checker verifier
pub struct SyntaxVerifier;

impl Verifier for SyntaxVerifier {
    fn verify(&self, dna: &EditDNA) -> VerificationResult {
        // Simplified: check token sequence validity
        let mut score = 1.0;
        let mut passed = true;
        let mut message = None;
        
        // Check for invalid sequences
        for window in dna.tokens.windows(2) {
            if let [EditToken::RemoveCall, EditToken::AddIf] = window {
                // This sequence might be problematic
                score -= 0.1;
            }
        }
        
        if score < 0.5 {
            passed = false;
            message = Some("Too many invalid token sequences".to_string());
        }
        
        VerificationResult {
            passed,
            score,
            checks: vec![CheckResult {
                name: "syntax".to_string(),
                passed,
                score,
                message,
            }],
        }
    }
}

/// Structure verifier
pub struct StructureVerifier;

impl Verifier for StructureVerifier {
    fn verify(&self, dna: &EditDNA) -> VerificationResult {
        // Check for balanced operations
        let adds = dna.tokens.iter().filter(|&&t| matches!(t, EditToken::AddIf | EditToken::AddLoop | EditToken::AddMatch)).count();
        let removes = dna.tokens.iter().filter(|&&t| matches!(t, EditToken::RemoveCall | EditToken::RemoveBranch)).count();
        
        let balance = 1.0 - ((adds as f64 - removes as f64).abs() / dna.tokens.len() as f64);
        let passed = balance > 0.5;
        
        VerificationResult {
            passed,
            score: balance,
            checks: vec![CheckResult {
                name: "structure".to_string(),
                passed,
                score: balance,
                message: None,
            }],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_patch_decoder() {
        let decoder = PatchDecoder::new();
        let dna = EditDNA::new(
            vec![EditToken::AddIf, EditToken::InsertGuard],
            crate::data::PatchCategory::BugFix,
        );
        let patch = decoder.decode(&dna);
        assert!(patch.contains("if condition"));
        assert!(patch.contains("if !condition"));
    }
    
    #[test]
    fn test_verifier_stack() {
        let mut stack = VerifierStack::new(0.5);
        stack.add_verifier(Box::new(SyntaxVerifier));
        stack.add_verifier(Box::new(StructureVerifier));
        
        let dna = EditDNA::new(vec![EditToken::AddIf], crate::data::PatchCategory::BugFix);
        let result = stack.verify(&dna);
        assert!(result.score > 0.0);
    }
}
