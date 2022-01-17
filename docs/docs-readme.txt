Docs readme, Gavin Pringle, 17 Jan 2022.

This folder contains two CompBioMed internal documentations and the one conference paper. 

The file polnet-cloud.doc contains "Cloud-based implementation of Software as a Service for HPC". This is the description by Malcolm Illingworth of the originally envisaged approach for the HOFF. 

The file polnet-cloud-implementation.doc contains "PolNet Computational Offload Service".  The description by Malcolm Illingworth of the actual implementation of the HOFF.

The CompBioMed 19 paper, also attached, is from the Computational Biomedicines 2019 conference, which is based on "PolNet Computational Offload Service" (above). The conference page: https://www.compbiomed-conference.org/cbmc19/

This Hoff Github repo which contains set-up instructions: https://github.com/EPCCed/hemelb-hoff/blob/main/hoff-setup-centos.txt. 

NB The HOFF currently is configured to use PBS but Cirrus has since moved to SLURM. Further, the HOFF is currently written in Python2 and would benefit from conversion to Python3. 

Finally, RADICAL SAGA is available from https://radical-cybertools.github.io/saga-python/index.html. SAGA is used by the HOFF to submit jobs to the underlying batch scheduler. It has adaptors for both PBS and SLURM.



  