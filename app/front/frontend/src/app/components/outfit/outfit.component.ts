import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ItemService } from '../../services/item.service';
@Component({
  selector: 'app-outfit',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './outfit.component.html',
  styleUrl: './outfit.component.css',
})
export class OutfitComponent implements OnInit{
  ropaLimpia: any[] = [];
  

  outfit: any = { sombrero: null, gafas: null, camiseta: null, pantalones: null, zapatos: null, chaqueta: null };
  locked: any = { sombrero: false, gafas: false, camiseta: false, pantalones: false, zapatos: false, chaqueta: false };


  slotsLayout = [
    { col: 1, id: 'sombrero', icon: '🎩' },
    { col: 1, id: 'gafas', icon: '👓' },
    { col: 2, id: 'camiseta', icon: '👕' },
    { col: 2, id: 'pantalones', icon: '👖' },
    { col: 2, id: 'zapatos', icon: '👟' },
    { col: 3, id: 'chaqueta', icon: '🧥' }
  ];

  constructor(private itemService: ItemService) {}

  ngOnInit() {
    this.cargarRopaLimpia();
  }

  cargarRopaLimpia() {
    this.itemService.getItems().subscribe(items => {
      this.ropaLimpia = items.filter(item => item.limpio);
    });
  }


  onGenerar() {
    if (this.ropaLimpia.length === 0) {
      alert("¡No tienes ropa limpia en tu colección!");
      return;
    }

    this.slotsLayout.forEach(slot => {

      if (!this.locked[slot.id]) {
        

        this.outfit[slot.id] = null;

        const idsUsados = Object.values(this.outfit)
          .filter((item: any) => item !== null)
          .map((item: any) => item.id);


        const ropaDisponible = this.ropaLimpia.filter(item => !idsUsados.includes(item.id));


        if (ropaDisponible.length > 0) {
          const randomItem = ropaDisponible[Math.floor(Math.random() * ropaDisponible.length)];
          this.outfit[slot.id] = randomItem;
        }
      }
    });
  }


  onRandomizeSingle(slotId: string) {
    if (this.locked[slotId] || this.ropaLimpia.length === 0) return;
    

    const idsUsados = Object.values(this.outfit)
      .filter((item: any) => item !== null)
      .map((item: any) => item.id);


    const ropaDisponible = this.ropaLimpia.filter(item => !idsUsados.includes(item.id));


    if (ropaDisponible.length === 0) {
      alert("No te quedan más prendas limpias diferentes para cambiar.");
      return;
    }


    const randomItem = ropaDisponible[Math.floor(Math.random() * ropaDisponible.length)];
    this.outfit[slotId] = randomItem;
  }


  toggleLock(slotId: string) {
    this.locked[slotId] = !this.locked[slotId];
  }


  onConfirmar() {
    const idsParaEnsuciar: number[] = [];
    

    for (const key in this.outfit) {
      if (this.outfit[key]) {
        idsParaEnsuciar.push(this.outfit[key].id);
      }
    }

    if (idsParaEnsuciar.length === 0) {
      alert("No hay prendas seleccionadas para confirmar.");
      return;
    }

    this.itemService.confirmOutfit(idsParaEnsuciar).subscribe(() => {
      // Limpiamos los huecos visuales
      this.outfit = { sombrero: null, gafas: null, camiseta: null, pantalones: null, zapatos: null, chaqueta: null };
      this.locked = { sombrero: false, gafas: false, camiseta: false, pantalones: false, zapatos: false, chaqueta: false };
      

      this.cargarRopaLimpia();
    });
  }
}
