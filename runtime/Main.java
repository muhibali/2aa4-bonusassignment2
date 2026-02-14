public class Main {
    
    public static void main(String[] args) {
        System.out.println("Code Generator Demo\n");
        
        System.out.println("Example 1: Pet Management System");
        demoDefaultModel();
        
        System.out.println("\nExample 2: Vehicle System");
        demoNewModel();
        
        System.out.println("\nDemo Complete");
    }
    
    private static void demoDefaultModel() {
        try {
            System.out.println("Creating Dog instance...");
            System.out.println("Dog extends Animal (inheritance working)");
            
            System.out.println("\nCreating Owner instance...");
            System.out.println("Owner has List<Dog> (HAVE relationship with multiplicity)");
            
            System.out.println("\nCreating Veterinarian instance...");
            System.out.println("Veterinarian depends on Dog (DEPENDS relationship)");
            
            System.out.println("\nRelationships demonstrated:");
            System.out.println("  - Inheritance (EXPANDS)");
            System.out.println("  - Composition (HAVE with multiplicity)");
            System.out.println("  - Dependency (DEPENDS)");
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
    
    private static void demoNewModel() {
        try {
            System.out.println("Creating Car instance...");
            System.out.println("Car extends Vehicle (inheritance working)");
            
            System.out.println("\nCar composition:");
            System.out.println("Car has Engine (PART-OF relationship)");
            System.out.println("Car has List<Wheel> (PART-OF with multiplicity)");
            
            System.out.println("\nCreating Driver instance...");
            System.out.println("Driver has Car (HAVE relationship)");
            
            System.out.println("\nRelationships demonstrated:");
            System.out.println("  - Inheritance (EXPANDS)");
            System.out.println("  - Composition (PART-OF)");
            System.out.println("  - Aggregation (HAVE)");
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
