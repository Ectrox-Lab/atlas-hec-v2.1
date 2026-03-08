//! Identity: 系统的永久身份标识
//! 
//! 这是 "this_is_me" anchor。
//! 一旦创建，永远不变。

use std::time::{SystemTime, UNIX_EPOCH};

/// 系统身份标识
#[derive(Clone, Debug, PartialEq)]
pub struct Identity {
    /// 唯一标识符: "atlas-v2.3-instance-001"
    pub id: String,
    
    /// 实例编号
    pub instance: u64,
    
    /// 创建时间戳 (Unix epoch seconds)
    pub created_at: u64,
}

impl Identity {
    /// 创建新身份
    /// 
    /// # 示例
    /// ```
    /// let identity = Identity::new(1);
    /// assert!(identity.id.starts_with("atlas-v2.3-instance-"));
    /// ```
    pub fn new(instance: u64) -> Self {
        let created_at = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        let id = format!("atlas-v2.3-instance-{:03}", instance);
        
        Self {
            id,
            instance,
            created_at,
        }
    }
    
    /// 返回身份字符串
    pub fn to_string(&self) -> String {
        self.id.clone()
    }
    
    /// 获取运行时间 (秒)
    pub fn uptime_seconds(&self) -> u64 {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        now.saturating_sub(self.created_at)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_identity_creation() {
        let identity = Identity::new(1);
        assert_eq!(identity.id, "atlas-v2.3-instance-001");
        assert_eq!(identity.instance, 1);
        assert!(identity.created_at > 0);
    }
    
    #[test]
    fn test_identity_format() {
        let identity = Identity::new(42);
        assert_eq!(identity.id, "atlas-v2.3-instance-042");
    }
}
