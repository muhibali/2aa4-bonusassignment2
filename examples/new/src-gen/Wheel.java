import java.util.List;
import java.util.ArrayList;

public class Wheel {

    // Fields
    private List<Car> cars;

    // Constructor
    public Wheel() {
        this.cars = new ArrayList<>();
    }

    // Getters and Setters
    public List<Car> getCars() {
        return cars;
    }

    public void setCars(List<Car> cars) {
        this.cars = cars;
    }

}