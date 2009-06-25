import FWCore.ParameterSet.Config as cms

process = cms.Process("PAT")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

# source
process.source = cms.Source("PoolSource", 
     fileNames = cms.untracked.vstring('/store/relval/CMSSW_3_1_0_pre10/RelValTTbar/GEN-SIM-RECO/IDEAL_31X_v1/0008/CC80B73A-CA57-DE11-BC2F-000423D99896.root')
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('IDEAL_31X::All')
process.load("Configuration.StandardSequences.MagneticField_cff")

# PAT Layer 0+1
process.load("PhysicsTools.PatAlgos.patSequences_cff")
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.inFlightMuons = cms.EDProducer("PATGenCandsFromSimTracksProducer",
        src           = cms.InputTag("g4SimHits"), # use "famosSimHits" for FAMOS
        setStatus     = cms.int32(-1),
        particleTypes = cms.vstring("mu+"),       # picks also mu-, of course
        filter        = cms.vstring("pt > 0.5"),  # just for testing
        makeMotherLink = cms.bool(True),
        writeAncestors = cms.bool(True), # save also the intermediate GEANT ancestors of the muons
        genParticles   = cms.InputTag("genParticles"),
)
process.muMatch3 = process.muonMatch.clone(mcStatus = cms.vint32(3))
process.muMatch1 = process.muonMatch.clone(mcStatus = cms.vint32(1))
process.muMatchF = process.muonMatch.clone(mcStatus = cms.vint32(-1),
                                           matched  = cms.InputTag("inFlightMuons"))
process.patDefaultSequence.replace(process.muonMatch, process.muMatch1+process.muMatch3+process.muMatchF)
process.allLayer1Muons.genParticleMatch = cms.VInputTag(
    cms.InputTag("muMatch3"),
    cms.InputTag("muMatch1"), 
    cms.InputTag("muMatchF"),
)

# replacements currently needed to make the jets work
process.allLayer1Jets.addDiscriminators    = False
process.allLayer1Jets.discriminatorSources = []

#process.content = cms.EDAnalyzer("EventContentAnalyzer")
process.p = cms.Path(
    process.inFlightMuons + 
    process.patDefaultSequence  
)

# Output module configuration
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('PATLayer1_Output.fromRECO_inFlight_full.root'),
    # save only events passing the full path
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    outputCommands = cms.untracked.vstring(
                'drop *', 
                'keep *_inFlightMuons_*_*',
                *patEventContent  # you need a '*' to unpack the list of commands 'patEventContent'
    )
)
process.outpath = cms.EndPath(process.out)

