#include <gazebo/gui/Plugin.hh>
#include <gazebo/gui/MainWindow.hh>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/empty.hpp>
#include <QVBoxLayout>
#include <QPushButton>
#include <QLabel>

namespace gazebo
{
  class SimControlPlugin : public GUIPlugin
  {
    Q_OBJECT

    public: SimControlPlugin() : GUIPlugin()
    {
      // --- Create the main widget ---
      auto mainWidget = new QWidget();
      auto layout = new QVBoxLayout();
      mainWidget->setLayout(layout);

      // --- Create ROS2 Node ---
      if (!rclcpp::is_initialized()) {
        rclcpp::init(0, nullptr);
      }
      this->ros_node_ = rclcpp::Node::make_shared("gazebo_gui_controller");
      this->restart_pub_ = this->ros_node_->create_publisher<std_msgs::msg::Empty>("/sim/restart", 1);
      this->stop_pub_ = this->ros_node_->create_publisher<std_msgs::msg::Empty>("/sim/stop", 1);

      // --- Create GUI Elements ---
      auto restartButton = new QPushButton("Restart Mission");
      connect(restartButton, &QPushButton::clicked, this, &SimControlPlugin::onRestartClicked);
      layout->addWidget(restartButton);

      auto stopButton = new QPushButton("Stop All Nodes");
      connect(stopButton, &QPushButton::clicked, this, &SimControlPlugin::onStopClicked);
      layout->addWidget(stopButton);

      layout->addWidget(new QLabel("---")); // Separator

      // Placeholder for thruster activity
      layout->addWidget(new QLabel("Thruster Activity:"));
      this->thruster_label_ = new QLabel("Forward: 0.0 | Turn: 0.0");
      layout->addWidget(this->thruster_label_);

      // --- Add the widget to the Gazebo GUI ---
      this->mainWindow = gazebo::gui::get_main_window();
      this->mainWindow->AddPanel("Sim Control", mainWidget);
    }

    private slots: void onRestartClicked()
    {
      auto msg = std_msgs::msg::Empty();
      this->restart_pub_->publish(msg);
      RCLCPP_INFO(this->ros_node_->get_logger(), "Restart button clicked!");
    }

    private slots: void onStopClicked()
    {
      auto msg = std_msgs::msg::Empty();
      this->stop_pub_->publish(msg);
      RCLCPP_INFO(this->ros_node_->get_logger(), "Stop button clicked!");
      // In a real system, a node would listen to this and shut down the launch file.
      // For now, it just logs a message.
    }

    private:
      gazebo::gui::MainWindow *mainWindow;
      rclcpp::Node::SharedPtr ros_node_;
      rclcpp::Publisher<std_msgs::msg::Empty>::SharedPtr restart_pub_;
      rclcpp::Publisher<std_msgs::msg::Empty>::SharedPtr stop_pub_;
      QLabel* thruster_label_;
  };

  // Register this plugin with Gazebo
  GZ_REGISTER_GUI_PLUGIN(SimControlPlugin)
}