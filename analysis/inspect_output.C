#include <TFile.h>
#include <TTree.h>
#include <TSystem.h>
#include <iostream>
#include <string>

// No interpreta filas de damage como número de primarios.
void inspect_output(const char* filename = "molecular-dna.root", Long64_t expectedPrimaries = -1) {
  TFile input(filename, "READ");
  if (input.IsZombie() || input.TestBit(TFile::kRecovered)) {
    std::cerr << "ERROR: ROOT ilegible o recuperado: " << filename << std::endl;
    gSystem->Exit(1);
    return;
  }
  const char* names[] = {"primary_source", "chromosome_hits", "classification", "source", "damage"};
  bool valid = true;
  for (auto name : names) {
    TTree* tree = nullptr;
    input.GetObject((std::string("tuples/") + name).c_str(), tree);
    if (!tree) {
      std::cerr << "Falta tuples/" << name << std::endl;
      valid = false;
    } else {
      std::cout << "tuples/" << name << ": " << tree->GetEntries() << " filas" << std::endl;
      if (std::string(name) == "primary_source" && expectedPrimaries >= 0 && tree->GetEntries() != expectedPrimaries) {
        std::cerr << "ERROR: primarios procesados distintos de los solicitados: " << expectedPrimaries << std::endl;
        valid = false;
      }
    }
  }
  // Un archivo de un worker puede tener cero filas en una prueba muy pequeña.
  gSystem->Exit(valid ? 0 : 1);
}
