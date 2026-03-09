//! Predictive model for proprioceptive feedback
//! 
//! Simple linear predictor for pressure/strain at next timestep.
//! Tests whether predictive self-model improves stability.

use nalgebra::{DVector, DMatrix};
use crate::mesh::SoftMesh;

/// Linear predictor: ŷ(t+1) = W · x(t) + b
pub struct LinearPredictor {
    pub weights: DMatrix<f32>,
    pub bias: DVector<f32>,
    pub input_dim: usize,
    pub output_dim: usize,
    pub learning_rate: f32,
}

impl LinearPredictor {
    pub fn new(input_dim: usize, output_dim: usize) -> Self {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        // Small random initialization
        let weights = DMatrix::from_fn(output_dim, input_dim, |_, _| {
            rng.gen::<f32>() * 0.01 - 0.005
        });
        let bias = DVector::from_element(output_dim, 0.0);
        
        Self {
            weights,
            bias,
            input_dim,
            output_dim,
            learning_rate: 0.001,
        }
    }
    
    /// Predict next state given current sensor readings
    pub fn predict(&self, input: &DVector<f32>) -> DVector<f32> {
        &self.weights * input + &self.bias
    }
    
    /// Update weights based on prediction error
    pub fn update(&mut self, input: &DVector<f32>, target: &DVector<f32>) -> f32 {
        let prediction = self.predict(input);
        let error = target - &prediction;
        let mse = error.norm_squared() / error.len() as f32;
        
        // Gradient descent: dL/dW = -2 * error * input^T
        let gradient = -&error * input.transpose() * 2.0 * self.learning_rate;
        self.weights += gradient;
        self.bias += &error * 2.0 * self.learning_rate;
        
        mse
    }
    
    /// Compute mean squared error
    pub fn mse(&self, predictions: &DVector<f32>, targets: &DVector<f32>) -> f32 {
        let diff = predictions - targets;
        diff.norm_squared() / diff.len() as f32
    }
}

/// Controller using predictive feedback
pub struct PredictiveController {
    pub predictor: LinearPredictor,
    pub target_pressure: f32,
    pub target_shape: Option<DVector<f32>>,
    pub history: Vec<Vec<f32>>,  // sensor history
    pub max_history: usize,
    pub total_error: f32,
    pub prediction_count: usize,
}

impl PredictiveController {
    pub fn new(num_sensors: usize, target_pressure: f32) -> Self {
        Self {
            predictor: LinearPredictor::new(num_sensors, num_sensors),
            target_pressure,
            target_shape: None,
            history: Vec::new(),
            max_history: 100,
            total_error: 0.0,
            prediction_count: 0,
        }
    }
    
    /// Extract sensor readings from mesh
    pub fn extract_sensors(&self, mesh: &SoftMesh) -> Vec<f32> {
        let strain = mesh.compute_strain();
        let centroid = mesh.centroid();
        let bounding = mesh.bounding_box();
        let volume = (bounding.1.x - bounding.0.x) * (bounding.1.y - bounding.0.y);
        
        // Sensor vector: [strain_0, ..., strain_n, centroid_x, centroid_y, volume]
        let mut sensors = strain;
        sensors.push(centroid.x);
        sensors.push(centroid.y);
        sensors.push(volume);
        sensors.push(mesh.pressure.pressure);  // current pressure setting
        
        sensors
    }
    
    /// Compute control action based on prediction error
    pub fn compute_action(&mut self, mesh: &mut SoftMesh, feedback_enabled: bool) -> f32 {
        let sensors = self.extract_sensors(mesh);
        
        // Store in history
        self.history.push(sensors.clone());
        if self.history.len() > self.max_history {
            self.history.remove(0);
        }
        
        if self.history.len() < 2 {
            return 0.0;  // Not enough history
        }
        
        // Get previous and current readings
        let prev: DVector<f32> = DVector::from_vec(self.history[self.history.len()-2].clone());
        let current: DVector<f32> = DVector::from_vec(sensors.clone());
        
        // Predict from previous
        let prediction = self.predictor.predict(&prev);
        
        // Compute prediction error
        let pred_error = &current - &prediction;
        let mse = pred_error.norm_squared() / pred_error.len().max(1) as f32;
        
        // Clamp MSE to prevent explosion
        let mse_clamped = mse.clamp(0.0, 10000.0);
        
        if mse_clamped.is_finite() {
            self.total_error += mse_clamped;
            self.prediction_count += 1;
        }
        
        // Update predictor
        self.predictor.update(&prev, &current);
        
        if !feedback_enabled {
            return mse_clamped;
        }
        
        // Use prediction for control (gentle adjustment)
        let pressure_error = self.target_pressure - sensors.last().copied().unwrap_or(0.0);
        let control_signal = pressure_error * 0.05;  // Simple proportional control
        
        // Adjust mesh pressure slowly
        let new_pressure = mesh.pressure.pressure + control_signal.clamp(-5.0, 5.0);
        mesh.pressure.pressure = new_pressure.clamp(20.0, 100.0);
        
        mse_clamped
    }
    
    /// Get average prediction error
    pub fn average_error(&self) -> f32 {
        if self.prediction_count == 0 {
            0.0
        } else {
            self.total_error / self.prediction_count as f32
        }
    }
    
    /// Reset statistics
    pub fn reset_stats(&mut self) {
        self.total_error = 0.0;
        self.prediction_count = 0;
    }
}

/// Baseline controller (reactive, no prediction)
pub struct ReactiveController {
    pub target_pressure: f32,
    pub kp: f32,  // proportional gain
}

impl ReactiveController {
    pub fn new(target_pressure: f32) -> Self {
        Self {
            target_pressure,
            kp: 0.1,
        }
    }
    
    pub fn compute_action(&self, mesh: &mut SoftMesh) {
        let current = mesh.pressure.pressure;
        let error = self.target_pressure - current;
        let new_pressure = current + error * self.kp;
        mesh.pressure.pressure = new_pressure.clamp(10.0, 200.0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::mesh::SoftMesh;
    use nalgebra::Vector2;
    
    #[test]
    fn test_predictor_creation() {
        let p = LinearPredictor::new(5, 5);
        assert_eq!(p.input_dim, 5);
        assert_eq!(p.output_dim, 5);
    }
    
    #[test]
    fn test_sensor_extraction() {
        let mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 1.0, 1.0, 4, 4);
        let controller = PredictiveController::new(20, 50.0);
        let sensors = controller.extract_sensors(&mesh);
        assert!(sensors.len() > 0);
    }
}
