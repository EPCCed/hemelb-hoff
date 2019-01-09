# hemelb-hoff: "HemelB High Performance Offload"


The aim of the hemelb-hoff project is to allow easy REST-based access to high performance computational resources such as EPCC's CIRRUS service and SURFSara's LISA service. It is intended to seamlessly integrate with the CompBioMed PolNet workflow suite.

## Detailed aims
The existing PolNet suite (implemented as MatLab scripts) supports a workflow that can be run locally on a user's workstation.
However, stages of this workflow can become computationally expensive and it would be advantageous to offload these expensive steps to more powerful remote services.  
In order to support this, hemelb-hoff implements a service that provides a set of REST endpoints for submitting and managing computational jobs on remote high performance resources. The REST endpoints can be accessed using any compatible REST client or library, such as the Python requests library.
The project has focussed on providing access to the HemelB software, but is intended to be general purpose.  

### Funding and organisation
This project is funded under CompBioMed, work package 5

### Links
PolNet: https://www.ncbi.nlm.nih.gov/pubmed/29742399  
CompBioMed: https://www.compbiomed.eu/  
EPCC: www.epcc.ed.ac.uk  
SURFSara: www.surfsara.nl

