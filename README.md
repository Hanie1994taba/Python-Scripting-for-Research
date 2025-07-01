# Python-Scripting-for-Research


## 🧩 Project Summary
This repository contains a Grasshopper-based computational design workflow and a Python script that implement a face-selection mechanism inspired by the research article:

> **Graph Neural Networks for Construction Applications**  
> Yilong Jia, Jun Wang, Wenchi Shou, M. Reza Hosseini, Yu Bai  
> *Automation in Construction, 2023*  
> [DOI: 10.1016/j.autcon.2023.104984](https://doi.org/10.1016/j.autcon.2023.104984)

The workflow simulates graph-based logic in the selection and evaluation of mesh faces for structurally informed design. While it does not implement a Graph Neural Network (GNN), it follows a similar rule-based, data-driven reasoning approach for spatial and structural decisions.

---

## 🎯 Purpose
The goal of this project is to:
- Implement construction-logic-aware mesh evaluation inspired by the GNN pipeline.
- Optimize face selection using parameters like mesh area, connectivity, and performance.
- Handle structural indeterminacy and topological irregularities (e.g., vertex-face overlaps).
- Propose a reproducible, adaptable design workflow using Grasshopper + Python + PolyFrame.

---

## 🧮 Input Parameters

| Input         | Type             | Description                                                                 |
|---------------|------------------|-----------------------------------------------------------------------------|
| `PF`          | PolyFrame object | Input polyhedral frame with faces, vertices, and edges                     |
| `reactions`   | Integer          | Number of external reactions used in the indeterminacy equation            |
| `performance` | List of floats   | Performance metric (per face), used to prioritize face selection           |
| `coef1`       | Float            | Weight for inverse normalized area (1 - area)                              |
| `coef2`       | Float            | Weight for number of edges in a face                                       |
| `coef3`       | Float            | Weight for performance metric                                              |

---

## ⚙️ Outputs

| Output Name        | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `raw_mesh`         | Mesh created from initially selected internal faces                         |
| `chosenfaces_ids`  | List of IDs of the selected faces based on indeterminacy and scoring        |
| `newly_added`      | List of additional faces added to resolve topological inconsistencies        |
| `combined_mesh`    | Final mesh output combining original and added faces, free of mesh errors    |

---

## 🔍 Algorithm Overview

### 1. **Face Preprocessing**
- Faces are filtered to exclude external ones.
- Areas are normalized between 0 and 1.

### 2. **Rating Formula**
Each internal face is assigned a score:
- score = (1 - normalized_area) * coef1 + coef2 * edge_count + coef3 * performance
  
### 3. **Indeterminacy Constraint**
Faces are added iteratively if they maintain or reduce the system's structural indeterminacy:
- indeterminancy = total_edges + reactions - 3 * total_vertices
  
### 4. **Topological Repair**
Absent edges are detected, and faces containing those edges are backtracked and selectively added to ensure completeness.

### 5. **Mesh Joining**
All selected faces and extra ones are combined.


### 6. **Vertex-Face Connectivity Check**
Vertices connected to more than 2 disconnected face components are detected and resolved by:
- Prioritizing elements via relational metrics
- Dynamically resolving inconsistencies.
- Iteratively refining the network structure.




