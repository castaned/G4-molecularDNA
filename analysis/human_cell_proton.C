// Adapted from Geant4 v11.3.0 human_cell.C for the human_cell geometry.
// Original four-panel plots and yield conventions retained.
// No automatic hadd; select ONE complete particle/energy task.
// Fragment pooling omitted; uncertainties are not estimated by this macro.
// See analysis/README.md for modifications, scope and validation status.
#include <TCanvas.h>
#include <TFile.h>
#include <TTree.h>
#include <TH1.h>
#include <TH1F.h>
#include <TGraph.h>
#include <TStyle.h>
#include <TPad.h>
#include <TROOT.h>
#include <TSystem.h>
#include <TMath.h>
#include <TAxis.h>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;
//-------------------------------------------------------------------------------//
// This macrofile was developed by Konstantinos Chatzipapas at LP2iB (ex. CENBG) //
// in collaboration with the whole team of molecularDNA Geant4-DNA example       //
// Publication: ....................................                             //
// For any question please contact through:                                      //
// chatzipa@cenbg.in2p3.fr (or k.chatzipapas@yahoo.com)                                                       //
//-------------------------------------------------------------------------------//

// This macro requires the molecular-dna.root file generated from molecularDNA example
// To run this file just insert this command to the terminal:
// root .X analysis.C
// ROOT6.x should be installed

//***************************************//
// Please define the parameters below    //
// ifile, r3, Nbp (as shown in terminal) //
//***************************************//

void human_cell_proton(const char* input = "molecular-dna.root", const char* output = "plots", double dnaMbp = 6405.886128) {
//**********//
// If you need to add multiple root outputs, by multithreading, use this command:

// Define these parameters of the simulation
const char* ifile = input;
Double_t r3 = 7100e-9 * 2500e-9 * 7100e-9; // human_cell.mac: semiaxes in metres
Double_t Nbp = dnaMbp; // Verify DNA length printed by the geometry
Double_t mass = 997 * 4 * 3.141592 * r3 / 3 ;  // waterDensity * 4/3 * pi * r3 in kg
///////////////////////////////////////////////////////////////////////////////////
//*******************************************************************************//

// Keep the ROOT session intact.
gStyle->SetPalette(1);
gROOT->SetStyle("Plain");
gStyle->SetOptStat(00000);

// Four panels adapted from the official example.
TCanvas *c1 = new TCanvas("c1", "Molecular DNA - Damage Quantification", 60, 120, 800, 800);
c1->SetBorderSize(0);
c1->SetFillColor(0);
c1->SetFillStyle(4000);
gPad->SetLeftMargin(0.13);

TPad* pad1 = new TPad("pad1","Species", 0, 0.51, 0.49, 1);
pad1->SetBorderSize(0);
pad1->SetFillColor(0);
pad1->SetFillStyle(4000);
pad1->SetLeftMargin(0.15);
pad1->SetRightMargin(0.01);
pad1->SetBottomMargin(0.2);

TPad* pad2 = new TPad("pad2","Damage Yield", 0.51, 0.5, 1, 1);
pad2->SetBorderSize(0);
pad2->SetFillColor(0);
pad2->SetFillStyle(4000);
pad2->SetLeftMargin(0.15);
pad2->SetRightMargin(0.05);
pad2->SetBottomMargin(0.2);

TPad* pad3 = new TPad("pad3","Breaks Yield SSB", 0, 0, 0.49, 0.49);
pad3->SetBorderSize(0);
pad3->SetFillColor(0);
pad3->SetFillStyle(4000);
pad3->SetLeftMargin(0.15);
pad3->SetRightMargin(0.01);
//pad3->SetTopMargin(0.2);
pad3->SetBottomMargin(0.2);

TPad* pad4 = new TPad("pad4","Breaks Yield DSB", 0.51, 0, 1, 0.49);
pad4->SetBorderSize(0);
pad4->SetFillColor(0);
pad4->SetFillStyle(4000);
pad4->SetLeftMargin(0.15);
pad4->SetRightMargin(0.05);
//pad3->SetTopMargin(0.2);
pad4->SetBottomMargin(0.2);

pad1->Draw();
pad2->Draw();
pad3->Draw();
pad4->Draw();

// Open root file
TFile *f = TFile::Open(ifile);
if (!f || f->IsZombie() || f->TestBit(TFile::kRecovered) || dnaMbp <= 0) {
  cerr << "Invalid input ROOT file or DNA length" << endl;
  return;
}
for (const char* name : {"primary_source", "damage", "classification", "source", "chromosome_hits"}) {
  if (!f->Get((string("tuples/") + name).c_str())) {
    cerr << "Missing tuples/" << name << endl;
    f->Close();
    return;
  }
}

// Initialize Variables
Int_t EB = 0, ES = 0, OHB = 0, OHS = 0, HB = 0, HS = 0, FL = 0;
Int_t total_EB = 0, total_ES = 0, total_OHB = 0, total_OHS = 0, total_HB = 0, total_HS = 0, total_FL = 0;
Float_t total_EB2 = 0, total_ES2 = 0, total_OHB2 = 0, total_OHS2 = 0, total_HB2 = 0, total_HS2 = 0, total_FL2 = 0;

Int_t SSB = 0, SSBp = 0, SSB2p = 0;
Int_t total_SSB = 0, total_SSBp = 0, total_SSB2p = 0;
Float_t total_SSB2 = 0, total_SSBp2 = 0, total_SSB2p2 = 0;
Int_t DSB = 0, DSBp = 0, DSBpp = 0;
Int_t total_DSB = 0, total_DSBp = 0, total_DSBpp = 0;
Float_t total_DSB2 = 0, total_DSBp2 = 0, total_DSBpp2 = 0;

Int_t SSBd = 0, SSBi = 0, SSBm = 0;
Int_t total_sSSB = 0, total_SSBd = 0, total_SSBi = 0, total_SSBm = 0;
Float_t total_sSSB2 = 0, total_SSBd2 = 0, total_SSBi2 = 0, total_SSBm2 = 0;
Int_t DSBd = 0, DSBi = 0, DSBm = 0, DSBh = 0;
Int_t total_sDSB = 0, total_DSBd = 0, total_DSBi = 0, total_DSBm = 0, total_DSBh = 0;
Float_t total_sDSB2 = 0, total_DSBd2 = 0, total_DSBi2 = 0, total_DSBm2 = 0, total_DSBh2 = 0;

Double_t dose = 0;

Double_t EB_yield = 0; Double_t ES_yield = 0; Double_t OHB_yield = 0; Double_t OHS_yield = 0; Double_t HB_yield = 0; Double_t HS_yield = 0;

Double_t SSB_yield = 0; Double_t SSBp_yield = 0; Double_t SSB2p_yield = 0;
Double_t DSB_yield = 0; Double_t DSBp_yield = 0; Double_t DSBpp_yield = 0;

Double_t sSSB_yield = 0; Double_t SSBi_yield = 0; Double_t SSBd_yield = 0; Double_t SSBm_yield = 0;
Double_t sDSB_yield = 0; Double_t DSBi_yield = 0; Double_t DSBd_yield = 0; Double_t DSBm_yield = 0; Double_t DSBh_yield = 0;

total_EB  = 0; total_ES = 0; total_OHB = 0; total_OHS = 0; total_HB = 0; total_HS = 0;

total_SSB  = 0; total_SSBp = 0; total_SSB2p = 0;
total_SSB2  = 0; total_SSBp2 = 0; total_SSB2p2 = 0;
total_DSB  = 0; total_DSBp = 0; total_DSBpp = 0;
total_DSB2  = 0; total_DSBp2 = 0; total_DSBpp2 = 0;

total_sSSB = 0; total_SSBd = 0; total_SSBi = 0; total_SSBm = 0;
total_sSSB2 = 0; total_SSBd2 = 0; total_SSBi2 = 0; total_SSBm2 = 0;
total_sDSB = 0; total_DSBd = 0; total_DSBi = 0; total_DSBm = 0; total_DSBh = 0;
total_sDSB2 = 0; total_DSBd2 = 0; total_DSBi2 = 0; total_DSBm2 = 0;  total_DSBh2 = 0;

Double_t eVtoJ = 1.60218e-19;
Double_t EnergyDeposited_eV = 0;
Double_t acc_edep = 0;
Double_t acc_edep2 = 0;

Double_t Energy = 0;
Double_t BPID = 0;

const char* primaryName = "proton"; // Selected entry point; input must match this particle
char *type= new char[256];

// Read trees and leaves from root file, and give values to variables
TTree* tree = (TTree*) f->Get("tuples/primary_source");
Double_t number = (Double_t) tree->GetEntries();
if (number < 2) { cerr << "Need at least two primaries; inspect worker/merged input" << endl; f->Close(); return; }



// For reading species production
tree = (TTree*) f->Get("tuples/damage");

tree->SetBranchAddress("Energy",            &Energy);
tree->SetBranchAddress("EaqBaseHits",       &EB);
tree->SetBranchAddress("EaqStrandHits",     &ES);
tree->SetBranchAddress("OHBaseHits",        &OHB);
tree->SetBranchAddress("OHStrandHits",      &OHS);
tree->SetBranchAddress("HBaseHits",         &HB);
tree->SetBranchAddress("HStrandHits",       &HS);
tree->SetBranchAddress("TypeClassification", type);
tree->SetBranchAddress("BasePair",          &BPID);


Long64_t nentries = tree->GetEntries();
for(int i = 0;i<nentries;i++){
  tree->GetEntry(i);

  total_EB   += EB;
  total_EB2  += pow(EB,2);
  total_ES   += ES;
  total_ES2  += pow(ES,2);
  total_OHB  += OHB;
  total_OHB2 += pow(OHB,2);
  total_OHS  += OHS;
  total_OHS2 += pow(OHS,2);
  total_HB   += HB;
  total_HB2  += pow(HB,2);
  total_HS   += HS;
  total_HS2  += pow(HS,2);



  }

// Fragment plot omitted: upstream pooling mixes independent events/chains.
// Uncertainties require a separate event/replica-level analysis.

// Read damage classification SSB, SSB+, 2SSB, DSB, DSB+, DSB++
// As they have been defined in: Nikjoo, H., O'Neill, O., Goodhead, T., & Terrissol, M. 1997,
// Computational modelling of low-energy electron-induced DNA damage by early physical
// and chemical events, International Journal of Radiation Biology, 71, 467.
tree = (TTree *) f->Get("tuples/classification");

tree->SetBranchAddress("Energy", &Energy);
tree->SetBranchAddress("SSB",    &SSB);
tree->SetBranchAddress("SSBp",   &SSBp);
tree->SetBranchAddress("2SSB",   &SSB2p);
tree->SetBranchAddress("DSB",    &DSB);
tree->SetBranchAddress("DSBp",   &DSBp);
tree->SetBranchAddress("DSBpp",  &DSBpp);


Long64_t nentriesC = tree->GetEntries();
for(int i = 0;i<nentriesC;i++){
  tree->GetEntry(i);

  total_SSBp   += SSBp;
  total_SSBp2  += pow(SSBp,2);
  total_SSB2p  += SSB2p;
  total_SSB2p2 += pow(SSB2p,2);
  total_SSB    += SSB;
  total_SSB2   += pow(SSB,2);

  total_DSBp   += DSBp;
  total_DSBp2  += pow(DSBp,2);
  total_DSBpp  += DSBpp;
  total_DSBpp2 += pow(DSBpp,2);
  total_DSB    += DSB;
  total_DSB2   += pow(DSB,2);

  }

// Uncertainties require a separate event/replica-level analysis.


// Read damage classification SSBd, SSBi, SSBm, DSBd, DSBi, DSBm, DSBh
// As they have been defined in: Nikjoo, H., O'Neill, O., Goodhead, T., & Terrissol, M. 1997,
// Computational modelling of low-energy electron-induced DNA damage by early physical
// and chemical events, International Journal of Radiation Biology, 71, 467.
tree = (TTree *) f->Get("tuples/source");

tree->SetBranchAddress("Energy", &Energy);
tree->SetBranchAddress("SSBd",   &SSBd);
tree->SetBranchAddress("SSBi",   &SSBi);
tree->SetBranchAddress("SSBm",   &SSBm);
tree->SetBranchAddress("DSBd",   &DSBd);
tree->SetBranchAddress("DSBi",   &DSBi);
tree->SetBranchAddress("DSBm",   &DSBm);
tree->SetBranchAddress("DSBh",   &DSBh);

Long64_t nentriesS = tree->GetEntries();
for(int i = 0;i<nentriesS;i++){
  tree->GetEntry(i);

  total_SSBd += SSBd;
  total_SSBd2 += pow((SSBd),2);
  total_SSBi += SSBi;
  total_SSBi2 += pow((SSBi),2);
  total_SSBm += SSBm;
  total_SSBm2 += pow((SSBm),2);
  total_sSSB += SSBd + SSBi + SSBm;
  total_sSSB2 += pow((SSBd+SSBi+SSBm),2);

  total_DSBd  += DSBd;
  total_DSBd2 += pow(DSBd,2);
  total_DSBi  += DSBi;
  total_DSBi2 += pow(DSBi,2);
  total_DSBm  += DSBm;
  total_DSBm2 += pow(DSBm,2);
  total_DSBh  += DSBh;
  total_DSBh2 += pow(DSBh,2);
  total_sDSB  += DSBd + DSBi + DSBm + DSBh;
  total_sDSB2 += pow((DSBd+DSBi+DSBm+DSBh),2);

  }

// Uncertainties require a separate event/replica-level analysis.



// Measure the Deposited Energy in the whole volume that includes DNA chain (chromosome)

tree = (TTree *) f->Get("tuples/chromosome_hits");
tree->SetBranchAddress("e_chromosome_kev",&EnergyDeposited_eV);
nentries = tree->GetEntries();
for(int i = 0;i<nentries;i++){
  tree->GetEntry(i);
  acc_edep += EnergyDeposited_eV *1e3;
  acc_edep2 += EnergyDeposited_eV *EnergyDeposited_eV *1e6;
}
tree->SetBranchAddress("e_dna_kev",&EnergyDeposited_eV);
nentries = tree->GetEntries();
for(int i = 0;i<nentries;i++){
  tree->GetEntry(i);
  acc_edep += EnergyDeposited_eV *1e3;
  acc_edep2 += EnergyDeposited_eV *EnergyDeposited_eV *1e6;
}

// Close the root file to free space
f->Close();

// Calculate the absorbed dose
dose = acc_edep * eVtoJ / mass;
if (!(dose > 0)) { cerr << "Zero deposited dose; cannot normalize yields" << endl; return; }

// This is a normalization factor to produce the output in Gy-1 Gbp-1, or else.
// Default value is 1 to produce the result in Gy-1 Mbp-1
// It changes Mbp to Gbp. Some other changes may be needed in graphs section (name of axes)
double norm = 1000;

// Calculate the yields, together with their standard deviation
EB_yield  = (Double_t) total_EB  / dose / Nbp;
ES_yield  = (Double_t) total_ES  / dose / Nbp;
OHB_yield = (Double_t) total_OHB / dose / Nbp;
OHS_yield = (Double_t) total_OHS / dose / Nbp;
HB_yield  = (Double_t) total_HB  / dose / Nbp;
HS_yield  = (Double_t) total_HS  / dose / Nbp;



SSB_yield   = (Double_t) norm * total_SSB   / dose / Nbp;
SSBp_yield  = (Double_t) norm * total_SSBp  / dose / Nbp;
SSB2p_yield = (Double_t) norm * total_SSB2p / dose / Nbp;

DSB_yield   = (Double_t) norm * total_DSB   / dose / Nbp;
DSBp_yield  = (Double_t) norm * total_DSBp  / dose / Nbp;
DSBpp_yield = (Double_t) norm * total_DSBpp / dose / Nbp;




sSSB_yield = (Double_t) norm * total_sSSB / dose / Nbp;
SSBi_yield = (Double_t) norm * total_SSBi / dose / Nbp;
SSBd_yield = (Double_t) norm * total_SSBd / dose / Nbp;
SSBm_yield = (Double_t) norm * total_SSBm / dose / Nbp;

sDSB_yield = (Double_t) norm * total_sDSB / dose / Nbp;
DSBi_yield = (Double_t) norm * total_DSBi / dose / Nbp;
DSBd_yield = (Double_t) norm * total_DSBd / dose / Nbp;
DSBm_yield = (Double_t) norm * total_DSBm / dose / Nbp;
DSBh_yield = (Double_t) norm * total_DSBh / dose / Nbp;




// Print output in terminal

float total_SSB_totalYield = SSB_yield + SSBp_yield + SSB2p_yield;
float total_DSB_totalYield = DSB_yield + DSBp_yield + DSBpp_yield;

cout<<"\n"                      <<ifile         <<'\n'
    <<"\nDose Absorbed (Gy): "  <<dose          <<'\n'
    <<"Particle : "             <<primaryName   <<'\t'
    <<"Energy (MeV) : "         <<Energy        <<'\t'
    <<"Number of Primaries : "  <<number        <<'\n'
    <<"  Output Damage : "                      <<'\n'<<'\t'
    <<"     Species Hits (Gy-1 Mbp-1) "      <<'\n'<<'\t'
    <<"EaqBaseHits   : "     <<EB_yield     <<"   \t"      <<" uncertainty: N/D"        <<'\n'<<'\t'
    <<"EaqStrandHits : "     <<ES_yield     <<"   \t"      <<" uncertainty: N/D"        <<'\n'<<'\t'
    <<"OHBaseHits    : "     <<OHB_yield    <<"   \t"      <<" uncertainty: N/D"      <<'\n'<<'\t'
    <<"OHStrandHits  : "     <<OHS_yield    <<"   \t"      <<" uncertainty: N/D"      <<'\n'<<'\t'
    <<"HBaseHits     : "     <<HB_yield     <<"   \t"      <<" uncertainty: N/D"        <<'\n'<<'\t'
    <<"HStrandHits   : "     <<HS_yield     <<"   \t"      <<" uncertainty: N/D"        <<'\n'<<'\n'<<'\t'
    <<"     Damage yield (Gy-1 Gbp-1) "      <<'\n'<<'\t'
    <<"SSB           : "     <<SSB_yield    <<"   \t"      <<" uncertainty: N/D"      <<'\n'<<'\t'
    <<"SSB+          : "     <<SSBp_yield   <<"   \t"      <<" uncertainty: N/D"    <<'\n'<<'\t'
    <<"2SSB          : "     <<SSB2p_yield  <<"   \t"      <<" uncertainty: N/D"  <<'\n'<<'\t'
    <<"SSB total     : "     <<total_SSB_totalYield        <<'\n'<<'\t'
    <<"DSB           : "     <<DSB_yield    <<"   \t"      <<" uncertainty: N/D"     <<'\n'<<'\t'
    <<"DSB+          : "     <<DSBp_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"DSB++         : "     <<DSBpp_yield  <<"   \t"      <<" uncertainty: N/D" <<'\n'<<'\t'
    <<"DSB total     : "     <<total_DSB_totalYield        <<'\n'<<'\n'<<'\t'
    <<"     Breaks yield (Gy-1 Gbp-1) "      <<'\n'<<'\t'
    <<"SSB direct    : "     <<SSBd_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"SSB indirect  : "     <<SSBi_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"SSB mixed     : "     <<SSBm_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"SSB total     : "     <<sSSB_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"DSB direct    : "     <<DSBd_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"DSB indirect  : "     <<DSBi_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"DSB mixed     : "     <<DSBm_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"DSB hybrid    : "     <<DSBh_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\t'
    <<"DSB total     : "     <<sDSB_yield   <<"   \t"      <<" uncertainty: N/D"   <<'\n'<<'\n'<<'\t'
    <<"SSB/DSB       : "     <<(sDSB_yield > 0 ? to_string(sSSB_yield/sDSB_yield) : string("N/D (DSB=0)"))       <<'\n'<<'\n';


// Plot Histograms

c1->GetCanvas()->cd();
pad1->cd();
const Int_t n = 6;
Double_t x[n] = {1,2,3,4,5,6};
Double_t y[n] = {EB_yield,ES_yield,OHB_yield,OHS_yield,HB_yield,HS_yield};
TGraph* gr = new TGraph(n,x,y);
gr->SetTitle("Species");
gr->GetXaxis()->SetBinLabel(9, "EaqBaseHits");
gr->GetXaxis()->SetBinLabel(25,"EaqStrandHits");
gr->GetXaxis()->SetBinLabel(42,"OHBaseHits");
gr->GetXaxis()->SetBinLabel(58,"OHStrandHits");
gr->GetXaxis()->SetBinLabel(75,"HBaseHits");
gr->GetXaxis()->SetBinLabel(92,"HStrandHits");
gr->GetYaxis()->SetTitle("Species Hits (Gy^{-1} Mbp^{-1})");
gr->GetYaxis()->SetTitleOffset(2);

gr->SetFillColor(49);
gr->Draw("ba");


pad2->cd();
Double_t x2[n] = {1,2,3,4,5,6};
Double_t y2[n] = {SSBp_yield,SSB2p_yield,SSB_yield,DSBp_yield,DSBpp_yield,DSB_yield};
TGraph* gr2 = new TGraph(n,x2,y2);
gr2->SetTitle("Damage Yield");
gr2->GetXaxis()->SetBinLabel(9, "SSB+");
gr2->GetXaxis()->SetBinLabel(25,"2SSB");
gr2->GetXaxis()->SetBinLabel(42,"SSB");
gr2->GetXaxis()->SetBinLabel(58,"DSB+");
gr2->GetXaxis()->SetBinLabel(75,"DSB++");
gr2->GetXaxis()->SetBinLabel(92,"DSB");
//gr2->GetYaxis()->SetTitle("Damage yield (Gy^{-1} Mbp^{-1})");
gr2->GetYaxis()->SetTitle("Damage yield (Gy^{-1} Gbp^{-1})");
gr2->GetYaxis()->SetTitleOffset(2);

gr2->SetFillColor(8);
gr2->Draw("ba");


pad3->cd();
const Int_t m = 4;
Double_t x3[m] = {1,2,3,4};
Double_t y3[m] = {SSBd_yield,SSBi_yield,SSBm_yield,sSSB_yield};
TGraph* gr3 = new TGraph(m,x3,y3);
gr3->SetTitle("Breaks Yield");
gr3->GetXaxis()->SetBinLabel(8, "SSB direct");
gr3->GetXaxis()->SetBinLabel(35,"SSB indirect");
gr3->GetXaxis()->SetBinLabel(64,"SSB mixed");
gr3->GetXaxis()->SetBinLabel(92,"SSB all");
//gr3->GetYaxis()->SetTitle("Breaks yield (Gy^{-1} Mbp^{-1})");
gr3->GetYaxis()->SetTitle("SSB yield (Gy^{-1} Gbp^{-1})");
gr3->GetYaxis()->SetTitleOffset(2);

gr3->SetFillColor(7);
gr3->Draw("ba");


pad4->cd();
const Int_t k = 5;
Double_t x4[k] = {1,2,3,4,5};
Double_t y4[k] = {DSBd_yield,DSBi_yield,DSBm_yield,DSBh_yield,sDSB_yield};
TGraph* gr4 = new TGraph(k,x4,y4);
gr4->SetTitle("Breaks Yield");
gr4->GetXaxis()->SetBinLabel(8,"DSB direct");
gr4->GetXaxis()->SetBinLabel(29,"DSB indirect");
gr4->GetXaxis()->SetBinLabel(50,"DSB mixed");
gr4->GetXaxis()->SetBinLabel(71,"DSB hybrid");
gr4->GetXaxis()->SetBinLabel(92,"DSB all");
//gr4->GetYaxis()->SetTitle("Breaks yield (Gy^{-1} Mbp^{-1})");
gr4->GetYaxis()->SetTitle("DSB yield (Gy^{-1} Gbp^{-1})");
gr4->GetYaxis()->SetTitleOffset(2);

gr4->SetFillColor(4);
gr4->Draw("ba");
gSystem->mkdir(output, true);
c1->SaveAs((string(output) + "/human_cell_proton.png").c_str());
c1->SaveAs((string(output) + "/human_cell_proton.pdf").c_str());
cout << "Uncertainty: not estimated. Central values only; evaluate uncertainty using independent replicas." << endl;
}
