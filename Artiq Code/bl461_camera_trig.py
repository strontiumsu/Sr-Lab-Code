# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 16:42:25 2022

@author: sr
"""

from artiq.experiment import *
import numpy as np
from fit_image import Fit2DGaussParabola
   
reps = 1

class BL461_camera_trig(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")
        self.setattr_device("ttl4")
        self.setattr_device("urukul1_cpld")
        self.setattr_device("sampler0")
        self.adc_0=self.get_device("sampler0")
    
    
        # Camera
        self.setattr_argument("t_exposure",NumberValue(50e-3,min=10e-3,max=300e-3,unit="ms",scale=1e-3),"Camera")  
        
        
        # 3D MOT AOM  
        self.setattr_argument("MOT3DDP_AOM_frequency",
            Scannable(default=[NoScan(100*1e6), RangeScan(85*1e6, 115*1e6, 10, randomize=False)],scale=1e6,
                      unit="MHz"),"MOT3DDP")

        self.setattr_argument("MOT3DDP_DDS_amplitude_scale",NumberValue(0.8,min=0.0,max=0.8),"MOT3DDP")
        self.setattr_argument("MOT3DDP_Urukul_attenuation",NumberValue(30.0,min=1.0,max=30.0),"MOT3DDP")
        
        # Zeeman slower AOM
        self.setattr_argument("ZeemanDP_AOM_frequency",
            Scannable(default=[NoScan(330*1e6), RangeScan(250*1e6, 350*1e6, 10, randomize=False)],scale=1e6,
                      unit="MHz"),"ZeemanDP")

        self.setattr_argument("ZeemanDP_DDS_amplitude_scale",NumberValue(0.8,min=0.0,max=0.95),"ZeemanDP")
        self.setattr_argument("ZeemanDP_Urukul_attenuation",NumberValue(30.0,min=0.0,max=30.0),"ZeemanDP")
        
        # 2D MOT AOM
        self.setattr_argument("MOT2D_AOM_frequency",
            Scannable(default=[NoScan(200*1e6), RangeScan(200*1e6, 200*1e6, 10, randomize=False)],scale=1e6,
                      unit="MHz"),"MOT2D")

        self.setattr_argument("MOT2D_DDS_amplitude_scale",NumberValue(0.8,min=0.0,max=0.8),"MOT2D")
        self.setattr_argument("MOT2D_Urukul_attenuation",NumberValue(30.0,min=1.0,max=30.0),"MOT2D")
        
        
        # Probe DP AOM
        self.setattr_argument("ProbeDP_AOM_frequency",
            Scannable(default=[NoScan(120*1e6), RangeScan(100*1e6, 140*1e6, 10, randomize=False)],scale=1e6,
                      unit="MHz"),"ProbeDP")

        self.setattr_argument("ProbeDP_DDS_amplitude_scale",NumberValue(0.8,min=0.0,max=0.8),"ProbeDP")
        self.setattr_argument("ProbeDP_Urukul_attenuation",NumberValue(30.0,min=1.0,max=30.0),"ProbeDP")
        
        
        # Urukul clock output syntonized to the RTIO clock.
        # Can be used as HMC830 reference on Sayma RTM.
        # When using this reference, Sayma must be recalibrated every time Urukul
        # is rebooted, as Urukul is not synchronized to the Kasli.
        self.urukul_hmc_ref_MOT2D = self.get_device("urukul1_ch0")
        self.urukul_hmc_ref_MOT3DDP = self.get_device("urukul1_ch1")
        self.urukul_hmc_ref_ZeemanDP = self.get_device("urukul1_ch2")
        self.urukul_hmc_ref_probeDP = self.get_device("urukul1_ch3")
        
        self.urukul_meas = [self.get_device("urukul1_ch0"),self.get_device("urukul1_ch1"),self.get_device("urukul1_ch2"),self.get_device("urukul1_ch3")]
        # The same waveform is output on all first 4 SAWG channels (first DAC).
        #self.flist = [i for i in range(140,240)]
       
       
        
    def prepare(self):
     
           #print(self.AOM_frequency.sequence)
           self.ZeemanDP_dds_scale=self.ZeemanDP_DDS_amplitude_scale
           self.MOT2D_dds_scale=self.MOT2D_DDS_amplitude_scale
           self.MOT3DDP_dds_scale=self.MOT3DDP_DDS_amplitude_scale
           self.probeDP_dds_scale=self.ProbeDP_DDS_amplitude_scale
           
           self.ZeemanDP_iatten=self.ZeemanDP_Urukul_attenuation
           self.MOT2D_iatten=self.MOT2D_Urukul_attenuation
           self.MOT3DDP_iatten=self.MOT3DDP_Urukul_attenuation
           self.probeDP_iatten=self.ProbeDP_Urukul_attenuation
           
           self.adc_data=[0.1 for ii in range(reps*len(self.ZeemanDP_AOM_frequency.sequence))]
          
         
                  
    @kernel
    def run(self):
            
            self.core.reset()
            delay(1*ms)

            self.urukul1_cpld.init()
            

            self.urukul_hmc_ref_MOT3DDP.init()
            self.urukul_hmc_ref_MOT3DDP.set_mu(0x40000000, asf=self.urukul_hmc_ref_MOT3DDP.amplitude_to_asf(self.MOT3DDP_dds_scale))
            self.urukul_hmc_ref_MOT3DDP.set_att(self.MOT3DDP_iatten)
            self.urukul_hmc_ref_MOT3DDP.sw.on()
            
            
            self.urukul_hmc_ref_ZeemanDP.init()
            self.urukul_hmc_ref_ZeemanDP.set_mu(0x40000000, asf=self.urukul_hmc_ref_ZeemanDP.amplitude_to_asf(self.ZeemanDP_dds_scale))
            self.urukul_hmc_ref_ZeemanDP.set_att(self.ZeemanDP_iatten)
            self.urukul_hmc_ref_ZeemanDP.sw.on()

            
            self.urukul_hmc_ref_MOT2D.init()
            self.urukul_hmc_ref_MOT2D.set_mu(0x40000000, asf=self.urukul_hmc_ref_MOT2D.amplitude_to_asf(self.MOT2D_dds_scale))
            self.urukul_hmc_ref_MOT2D.set_att(self.MOT2D_iatten)
            self.urukul_hmc_ref_MOT2D.sw.on()
            
            
            self.urukul_hmc_ref_probeDP.init()
            self.urukul_hmc_ref_probeDP.set_mu(0x40000000, asf=self.urukul_hmc_ref_probeDP.amplitude_to_asf(self.probeDP_dds_scale))
            self.urukul_hmc_ref_probeDP.set_att(self.probeDP_iatten)
            self.urukul_hmc_ref_probeDP.sw.on()
            

            ## Scan Zeeman double pass AOM
            
            # urukul_ch =self.urukul_meas[3]
                    
            # urukul_ch.init()
                    
            # urukul_ch.set_att(self.ZeemanDP_iatten)
            # urukul_ch.sw.on()
            
            # for kk in range(8500):
            #     for ii in range(len(self.ZeemanDP_AOM_frequency.sequence)):
                     
            #         fZeemanDP = self.ZeemanDP_AOM_frequency.sequence[ii]
            #         dds_ftw_ZeemanDP=self.urukul_meas[3].frequency_to_ftw(fZeemanDP)
            #         delay(2*ms)
            #         urukul_ch.set_mu(dds_ftw_ZeemanDP, asf=urukul_ch.amplitude_to_asf(self.ZeemanDP_dds_scale))
                
            fZeemanDP = self.ZeemanDP_AOM_frequency.sequence[0]
            dds_ftw_ZeemanDP=self.urukul_meas[2].frequency_to_ftw(fZeemanDP)
                
            urukul_ch =self.urukul_meas[2]

            urukul_ch.init()
            urukul_ch.set_mu(dds_ftw_ZeemanDP, asf=urukul_ch.amplitude_to_asf(self.ZeemanDP_dds_scale))
            urukul_ch.set_att(self.ZeemanDP_iatten)
            urukul_ch.sw.on()
                            
                
            fMOT2D = self.MOT2D_AOM_frequency.sequence[0]
            dds_ftw_MOT2D=self.urukul_meas[0].frequency_to_ftw(fMOT2D)
                
            urukul_ch =self.urukul_meas[0]

            urukul_ch.init()
            urukul_ch.set_mu(dds_ftw_MOT2D, asf=urukul_ch.amplitude_to_asf(self.MOT2D_dds_scale))
            urukul_ch.set_att(self.MOT2D_iatten)
            urukul_ch.sw.on() 
            
            
            # fprobeDP = self.ProbeDP_AOM_frequency.sequence[0]
            # dds_ftw_probeDP=self.urukul_meas[3].frequency_to_ftw(fprobeDP)
            
            # urukul_ch =self.urukul_meas[3]

            # urukul_ch.init()
            # urukul_ch.set_mu(dds_ftw_probeDP, asf=urukul_ch.amplitude_to_asf(self.probeDP_dds_scale))
            # urukul_ch.set_att(self.probeDP_iatten)
            # urukul_ch.sw.on()
            
            
            
            
            fMOT3DDP = self.MOT3DDP_AOM_frequency.sequence[0]
            dds_ftw_MOT3DDP=self.urukul_meas[1].frequency_to_ftw(fMOT3DDP)
            
            urukul_ch =self.urukul_meas[1]

            urukul_ch.init()
            urukul_ch.set_mu(dds_ftw_MOT3DDP, asf=urukul_ch.amplitude_to_asf(self.MOT3DDP_dds_scale))
            urukul_ch.set_att(self.MOT3DDP_iatten)
            urukul_ch.sw.on()
            
            
            
            urukul_ch =self.urukul_meas[3]
                    
            urukul_ch.init()
                    
            urukul_ch.set_att(self.probeDP_iatten)
            urukul_ch.sw.on()
            
            for kk in range(8500):
                for ii in range(len(self.ProbeDP_AOM_frequency.sequence)):
                     
                    fprobeDP = self.ProbeDP_AOM_frequency.sequence[ii]
                    dds_ftw_probeDP=self.urukul_meas[3].frequency_to_ftw(fprobeDP)
                    delay(2*ms)
                    urukul_ch.set_mu(dds_ftw_probeDP, asf=urukul_ch.amplitude_to_asf(self.probeDP_dds_scale))
            
            
            # urukul_ch =self.urukul_meas[1]
                    
            # urukul_ch.init()
                    
            # urukul_ch.set_att(self.MOT3DDP_iatten)
            # urukul_ch.sw.on()

            
            
            # urukul_ch =self.urukul_meas[1]
                    
            # urukul_ch.init()
                    
            # urukul_ch.set_att(self.MOT3DDP_iatten)
            # urukul_ch.sw.on()
            
            # for kk in range(8500):
            #     for ii in range(len(self.MOT3DDP_AOM_frequency.sequence)):
                     
            #         fMOT3DDP = self.MOT3DDP_AOM_frequency.sequence[ii]
            #         dds_ftw_MOT3DDP=self.urukul_meas[1].frequency_to_ftw(fMOT3DDP)
            #         delay(2*ms)
            #         urukul_ch.set_mu(dds_ftw_MOT3DDP, asf=urukul_ch.amplitude_to_asf(self.MOT3DDP_dds_scale))
         
            