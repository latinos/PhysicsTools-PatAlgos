import FWCore.ParameterSet.Config as cms

process = cms.Process("PAT")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.append('PATSummaryTables')
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
    default          = cms.untracked.PSet( limit = cms.untracked.int32( 1) ),
    PATSummaryTables = cms.untracked.PSet( limit = cms.untracked.int32(-1) )
)
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

# source
process.source = cms.Source("PoolSource", 
    fileNames = cms.untracked.vstring(
    'file:/afs/cern.ch/user/h/hegner/public/test2.root'
   #'rfio:/castor/cern.ch/cms/store/relval/CMSSW_3_1_0_pre4/RelValTTbar/GEN-SIM-RECO/IDEAL_30X_v1/0003/00E48100-3A16-DE11-A693-001617DBCF6A.root'
    )
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('IDEAL_30X::All')
process.load("Configuration.StandardSequences.MagneticField_cff")

# extraction of electron sequences
process.load("PhysicsTools.PatAlgos.recoLayer0.photonId_cff")
process.load("PhysicsTools.PatAlgos.recoLayer0.photonIsolation_cff")
process.load("PhysicsTools.PatAlgos.mcMatchLayer0.mcMatchSequences_cff")
process.load("PhysicsTools.PatAlgos.producersLayer1.photonProducer_cfi")
process.allLayer1Photons.addTrigMatch = False
#process.content = cms.EDAnalyzer("EventContentAnalyzer")

process.p = cms.Path(
    process.patPhotonIsolation * 
    process.photonMatch *        
    process.allLayer1Photons     
#   process.content
)

# Output module configuration
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('PATLayer1_Output.fromAOD_full.root'),
    # save only events passing the full path
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    # save PAT Layer 1 output
    outputCommands = cms.untracked.vstring('drop *', *patEventContent ) # you need a '*' to unpack the list of commands 'patEventContent'
)
process.outpath = cms.EndPath(process.out)

