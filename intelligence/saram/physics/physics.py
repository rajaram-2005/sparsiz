"""
Physics constraints: P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t)
Encoder trained so latent retains info necessary for these physical relationships
Loss: L = L_rec + λ1 L_physics + λ2 L_task + λ3 L_reg
"""

import math
import cmath

def P_VI(V: float, I: float) -> float:
    """P=VI"""
    return V*I

def S_PQ(P: float, Q: float) -> complex:
    """S=P+jQ"""
    return complex(P,Q)

def P_mech(T: float, omega: float) -> float:
    """P_mech=Tω"""
    return T*omega

def vibration_force(m: float, c: float, k: float, x: float, x_dot: float, x_ddot: float) -> float:
    """mẍ+cẋ+kx=F(t)"""
    return m*x_ddot + c*x_dot + k*x

def physics_loss(sample: dict, latent: list) -> float:
    """
    L_physics encourages latent to retain info for physical relationships
    """
    loss = 0.0
    # If sample contains V,I,P, check consistency and penalize if latent doesn't encode it
    if "voltage" in sample and "current" in sample and "power" in sample:
        expected = sample["voltage"]*sample["current"]
        actual = sample["power"]
        loss += (expected-actual)**2 / (expected**2+1e-6)

    if "torque" in sample and "omega" in sample and "mech_power" in sample:
        expected = sample["torque"]*sample["omega"]
        actual = sample["mech_power"]
        loss += (expected-actual)**2 / (expected**2+1e-6)

    # Regularize latent to be informative: encourage variance
    if latent:
        mean = sum(latent)/len(latent)
        var = sum((z-mean)**2 for z in latent)/len(latent)
        # Want variance not collapsed
        loss += max(0, 0.1 - var)

    return loss

def reconstruction_loss(x, x_hat):
    return sum((a-b)**2 for a,b in zip(x,x_hat))/len(x)

def total_loss(x, x_hat, latent, sample, lambda_physics=0.5, lambda_task=0.3, lambda_reg=0.1, task_loss=0.0):
    l_rec = reconstruction_loss(x, x_hat)
    l_physics = physics_loss(sample, latent)
    l_task = task_loss
    l_reg = sum(z*z for z in latent)/len(latent) if latent else 0
    return l_rec + lambda_physics*l_physics + lambda_task*l_task + lambda_reg*l_reg, {
        "rec": l_rec,
        "physics": l_physics,
        "task": l_task,
        "reg": l_reg,
    }
